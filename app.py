import streamlit as st
import numpy as np

# Function to perform structural verification
def structural_verification(largura, altura, espessura, comprimento, fy, le_x, le_y, Lx, Ly, Lz, Kx, Ky, Kz, N, Mx, My, Vx, Vy):

    # Propriedades geométricas
    A = 2 * largura * espessura + altura * espessura  # mm²
    Ix = (largura * altura**3)/12 - ((largura - espessura)*(altura - 2*espessura)**3)/12  # mm4
    Iy = (2 * espessura * largura**3)/12 + (altura * espessura**3)/12  # mm4
    Wx = Ix / (altura/2)  # mm3
    Wy = Iy / (largura/2)  # mm3
    rx = (Ix/A)**0.5  # mm
    ry = (Iy/A)**0.5  # mm

    # Verificação à tração/compressão (NBR 8800 - 5.1)
    def resistencia_compressao(A, fy, le_x, le_y, rx, ry, E=205000):
        # Índice de esbeltez
        λx = le_x/rx
        λy = le_y/ry

        # Força crítica de flambagem elástica
        Nex = (np.pi**2 * E * Ix)/(le_x**2) if le_x > 0 else float('inf')
        Ney = (np.pi**2 * E * Iy)/(le_y**2) if le_y > 0 else float('inf')

        # Parâmetro de flambagem
        λ0x = (A * fy/Nex)**0.5 if Nex > 0 else 0
        λ0y = (A * fy/Ney)**0.5 if Ney > 0 else 0

        # Fator de redução χ
        χx = 1/(0.658**(λ0x**2)) if λ0x <= 1.5 else 0.877/(λ0x**2)
        χy = 1/(0.658**(λ0y**2)) if λ0y <= 1.5 else 0.877/(λ0y**2)

        # Resistência de cálculo
        Nc_rdx = χx * A * fy / 1.1
        Nc_rdy = χy * A * fy / 1.1

        return min(Nc_rdx, Nc_rdy)

    Nc_rd = resistencia_compressao(A, fy, le_x, le_y, rx, ry)
    Nt_rd = A * fy / 1.1  # Resistência à tração

    # Verificação à flexão (NBR 8800 - 5.4)
    def resistencia_flexao(W, fy, Lb, Cb=1.0, E=205000, G=78925, J=None, Cw=None):
        # Flambagem lateral com torção (FLT)
        Lp = 1.76 * ry * (E/fy)**0.5
        if J is None:  # Simplificação para perfis U
            J = (2*largura*espessura**3 + (altura-2*espessura)*espessura**3)/3
        if Cw is None:  # Simplificação para perfis U
            Cw = (largura**3 * altura**2 * espessura)/12

        Lr = 1.95 * (E/(0.7*fy)) * (J/(A*(ry**0.5))) * (1 + (1 + 6.76*(0.7*fy/E * (Lb/ry)**2)**0.5))**0.5

        if Lb <= Lp:
            Mn = W * fy
        elif Lb <= Lr:
            Mn = Cb * (W * fy - (W * fy - 0.7*W*fy)*((Lb-Lp)/(Lr-Lp)))
        else:
            Fcr = (Cb * np.pi**2 * E)/(Lb/ry)**2 * (1 + 0.078 * J/(A * (ry**2)) * (Lb/ry)**2)**0.5
            Mn = Fcr * W

        return Mn / 1.1

    Mx_rd = resistencia_flexao(Wx, fy, Lz)
    My_rd = resistencia_flexao(Wy, fy, Lz)

    # Verificação ao cisalhamento (NBR 8800 - 5.5)
    def resistencia_cisalhamento(Aw, fy):
        return 0.6 * Aw * fy / 1.1

    Vx_rd = resistencia_cisalhamento(altura * espessura, fy)
    Vy_rd = resistencia_cisalhamento(2 * largura * espessura, fy)

    # Verificação combinada (NBR 8800 - 5.6)
    def verificacao_combinada(Nsd, Nrd, Mx_sd, Mx_rd, My_sd, My_rd):
        # Para flexo-compressão
        if Nsd > 0:
            ratio = Nsd/Nrd + 0.85*(Mx_sd/Mx_rd + My_sd/My_rd)
        # Para flexo-tração
        else:
            ratio = abs(Nsd)/Nrd + (Mx_sd/Mx_rd + My_sd/My_rd)
        return ratio

    ratio = verificacao_combinada(N, Nc_rd if N >=0 else Nt_rd, Mx, Mx_rd, My, My_rd)

    # Verificação de flambagem local (aba e alma)
    def flambagem_local(b, t, fy, elemento="alma"):
        if elemento == "alma":
            limite = 42 if fy == 250 else (35 if fy == 350 else (30 if fy == 420 else 42))
        else: # aba
            limite = 12 if fy == 250 else (10 if fy == 350 else (9 if fy == 420 else 12))

        return b/t <= limite

    ok_alma = flambagem_local(altura-2*espessura, espessura, fy, "alma")
    ok_aba = flambagem_local(largura, espessura, fy, "aba")

    return {
        "Nc_rd": Nc_rd,
        "Nt_rd": Nt_rd,
        "Mx_rd": Mx_rd,
        "My_rd": My_rd,
        "Vx_rd": Vx_rd,
        "Vy_rd": Vy_rd,
        "ratio": ratio,
        "ok_alma": ok_alma,
        "ok_aba": ok_aba
    }

# Streamlit app
def main():
    st.title("Verificação de Perfil U Enrijecido")

    # User input
    largura = st.number_input("Largura da aba (mm)", value=50.0)
    altura = st.number_input("Altura da alma (mm)", value=100.0)
    espessura = st.number_input("Espessura (mm)", value=2.0)
    comprimento = st.number_input("Comprimento (mm)", value=3000.0)
    fy = st.number_input("Resistência do aço (MPa)", value=250.0)
    le_x = st.number_input("Comprimento de flambagem em x (mm)", value=2500.0)
    le_y = st.number_input("Comprimento de flambagem em y (mm)", value=2500.0)
    Lx = st.number_input("Lx (mm)", value=3000.0)
    Ly = st.number_input("Ly (mm)", value=3000.0)
    Lz = st.number_input("Lz (mm)", value=3000.0)
    Kx = st.number_input("Coeficiente Kx", value=1.0)
    Ky = st.number_input("Coeficiente Ky", value=1.0)
    Kz = st.number_input("Coeficiente Kz", value=1.0)
    N = st.number_input("Carga axial N (kN)", value=50.0) * 1000  # Convert kN to N
    Mx = st.number_input("Momento fletor em x (kN.m)", value=10.0) * 1e6  # Convert kN.m to N.mm
    My = st.number_input("Momento fletor em y (kN.m)", value=5.0) * 1e6  # Convert kN.m to N.mm
    Vx = st.number_input("Força cortante em x (kN)", value=20.0) * 1000  # Convert kN to N
    Vy = st.number_input("Força cortante em y (kN)", value=15.0) * 1000  # Convert kN to N

    # Perform verification
    results = structural_verification(largura, altura, espessura, comprimento, fy, le_x, le_y, Lx, Ly, Lz, Kx, Ky, Kz, N, Mx, My, Vx, Vy)

    # Display results
    st.subheader("Resultados da Verificação Estrutural")
    st.write(f"Resistência de cálculo à compressão (Nc,Rd): {results['Nc_rd']/1000:.2f} kN")
    st.write(f"Resistência de cálculo à tração (Nt,Rd): {results['Nt_rd']/1000:.2f} kN")
    st.write(f"Resistência de cálculo à flexão em x (Mx,Rd): {results['Mx_rd']/1e6:.2f} kN.m")
    st.write(f"Resistência de cálculo à flexão em y (My,Rd): {results['My_rd']/1e6:.2f} kN.m")
    st.write(f"Resistência de cálculo ao cisalhamento em x (Vx,Rd): {results['Vx_rd']/1000:.2f} kN")
    st.write(f"Resistência de cálculo ao cisalhamento em y (Vy,Rd): {results['Vy_rd']/1000:.2f} kN")

    st.write("---")
    st.write(f"Verificação combinada (N + Mx + My): {results['ratio']:.3f} {'✅ (OK)' if results['ratio'] <= 1 else '❌ (Não OK)'}")

    st.write("---")
    st.write("**Verificação de flambagem local:**")
    st.write(f"- Alma (h/t): {(altura-2*espessura)/espessura:.1f} ≤ {42 if fy == 250 else (35 if fy == 350 else (30 if fy == 420 else 42))} {'✅ (OK)' if results['ok_alma'] else '❌ (Não OK)'}")
    st.write(f"- Aba (b/t): {largura/espessura:.1f} ≤ {12 if fy == 250 else (10 if fy == 350 else (9 if fy == 420 else 12))} {'✅ (OK)' if results['ok_aba'] else '❌ (Não OK)'}")

    # LaTeX report generation
    if st.button("Gerar Relatório LaTeX"):
        latex_code = f"""
\\documentclass[12pt]{{article}}
\\usepackage{{amsmath,graphicx}}
\\title{{Relatório de Verificação do Perfil U Enrijecido}}
\\begin{{document}}
\\maketitle
\\section*{{Dados de Entrada}}
\\begin{{itemize}}
    \\item Altura da alma: {altura} mm
    \\item Largura da aba: {largura} mm
    \\item Espessura: {espessura} mm
    \\item Comprimento: {comprimento} mm
    \\item Resistência do aço: {fy} MPa
    \\item Comprimentos de flambagem: Lx={Lx} mm, Ly={Ly} mm, Lz={Lz} mm
    \\item Coeficientes: Kx={Kx}, Ky={Ky}, Kz={Kz}
    \\item Cargas solicitantes: N={N/1000:.2f} kN, Mx={Mx/1e6:.2f} kN.m, My={My/1e6:.2f} kN.m, Vx={Vx/1000:.2f} kN, Vy={Vy/1000:.2f} kN
\\end{{itemize}}

\\section*{{Propriedades Geométricas}}
\\begin{{itemize}}
    \\item Área: {2 * largura * espessura + altura * espessura:.2f} mm²
    \\item Momento de inércia Ix: {((largura * altura**3)/12 - ((largura - espessura)*(altura - 2*espessura)**3)/12):.2f} mm⁴
    \\item Momento de inércia Iy: {(2 * espessura * largura**3)/12 + (altura * espessura**3)/12:.2f} mm⁴
    \\item Módulo resistente Wx: {(((largura * altura**3)/12 - ((largura - espessura)*(altura - 2*espessura)**3)/12) / (altura/2)):.2f} mm³
    \\item Módulo resistente Wy: {((2 * espessura * largura**3)/12 + (altura * espessura**3)/12) / (largura/2):.2f} mm³
    \\item Raio de giração rx: {(((largura * altura**3)/12 - ((largura - espessura)*(altura - 2*espessura)**3)/12) / (2 * largura * espessura + altura * espessura))**0.5:.2f} mm
    \\item Raio de giração ry: {((2 * espessura * largura**3)/12 + (altura * espessura**3)/12) / (2 * largura * espessura + altura * espessura))**0.5:.2f} mm
\\end{{itemize}}

\\section*{{Verificação Estrutural}}
\\begin{{itemize}}
    \\item Resistência à compressão: {results['Nc_rd']/1000:.2f} kN
    \\item Resistência à tração: {results['Nt_rd']/1000:.2f} kN
    \\item Resistência à flexão em x: {results['Mx_rd']/1e6:.2f} kN.m
    \\item Resistência à flexão em y: {results['My_rd']/1e6:.2f} kN.m
    \\item Resistência ao cisalhamento em x: {results['Vx_rd']/1000:.2f} kN
    \\item Resistência ao cisalhamento em y: {results['Vy_rd']/1000:.2f} kN
    \\item Verificação combinada: {results['ratio']:.3f} {'\\textcolor{{green}}{{(OK)}}' if results['ratio'] <= 1 else '\\textcolor{{red}}{{(Não OK)}}'}
    \\item Flambagem local da alma: {'\\textcolor{{green}}{{(OK)}}' if results['ok_alma'] else '\\textcolor{{red}}{{(Não OK)}}'}
    \\item Flambagem local da aba: {'\\textcolor{{green}}{{(OK)}}' if results['ok_aba'] else '\\textcolor{{red}}{{(Não OK)}}'}
\\end{{itemize}}
\\end{{document}}
"""
        st.code(latex_code, language="latex")

        tex_filename = "relatorio_perfil_U_enrijecido.tex"
        with open(tex_filename, "w", encoding="utf-8") as f:
            f.write(latex_code)
        st.success(f"Relatório LaTeX salvo como {tex_filename}")

if __name__ == "__main__":
    main()
