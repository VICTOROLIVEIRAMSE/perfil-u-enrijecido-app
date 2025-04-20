import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO
import sympy as sp
import tempfile
import os
from pylatex import Document, Section, Subsection, Math, Tabular, Figure, Command
from pylatex.utils import italic, bold

# Configuração inicial do Streamlit
st.set_page_config(page_title="Dimensionamento de Perfis Metálicos", layout="wide")
st.title("Dimensionamento de Perfis Metálicos - NBR 14762:2001")

# Funções de cálculo
def calcular_propriedades_geometricas(bf, bw, D, t, rm):
    """Calcula propriedades geométricas do perfil U enrijecido"""
    A = t * (2*bf + bw + 2*D)  # Área bruta
    Ix = (t * (2*bf**3 + bw**3 + 6*bf*bw**2 + 6*bf*D**2)) / 12  # Momento de inércia em x
    Iy = (t * (2*bf**3 + 6*bf*bw**2 + 6*bf*D**2)) / 12  # Momento de inércia em y
    It = (t**3 * (2*bf + bw + 2*D)) / 3  # Momento de inércia à torção
    Cw = (bf**2 * bw**2 * t) / 24  # Constante de empenamento
    
    rx = np.sqrt(Ix/A)  # Raio de giração em x
    ry = np.sqrt(Iy/A)  # Raio de giração em y
    
    # Centro de torção (simplificado para perfil U)
    x0 = bf/2 + t/2
    y0 = 0
    r0 = np.sqrt(rx**2 + ry**2 + x0**2 + y0**2)  # Raio de giração polar
    
    return {
        'A': A,
        'Ix': Ix,
        'Iy': Iy,
        'It': It,
        'Cw': Cw,
        'rx': rx,
        'ry': ry,
        'x0': x0,
        'y0': y0,
        'r0': r0
    }

def calcular_ne(E, I, K, L):
    """Calcula a força normal de flambagem elástica"""
    return (np.pi**2 * E * I) / (K * L)**2

def calcular_net(E, Cw, G, It, Kt, Lt, r0):
    """Calcula a força normal de flambagem por torção"""
    return (1/r0**2) * ((np.pi**2 * E * Cw)/(Kt * Lt)**2 + G * It)

def calcular_next(Nex, Net, x0, r0):
    """Calcula a força normal de flambagem por flexo-torção para perfis monossimétricos"""
    denominator = 2 * (1 - (x0/r0)**2)
    sqrt_part = np.sqrt(1 - (4 * Nex * Net * (1 - (x0/r0)**2)) / (Nex + Net)**2)
    return ((Nex + Net) / denominator) * (1 - sqrt_part)

def calcular_lambda0(Aef, fy, Ne):
    """Calcula o índice de esbeltez reduzido"""
    return np.sqrt(Aef * fy / Ne)

def calcular_fator_reducao(l0, alpha):
    """Calcula o fator de redução ρ conforme NBR 14762"""
    beta = 0.5 * (1 + alpha * (l0 - 0.2) + l0**2)
    rho = 1 / (beta + np.sqrt(beta**2 - l0**2))
    return min(rho, 1.0)

def calcular_larguras_efetivas_compressao(b, t, sigma, E, k):
    """Calcula larguras efetivas para elementos sob compressão"""
    lambda_p = (b/t) / (0.95 * np.sqrt(k * E / sigma))
    if lambda_p <= 0.673:
        return b
    else:
        return b * (1 - 0.22/lambda_p) / lambda_p

def verificar_flambagem_distorcional(bf, bw, D, t, fy, E):
    """Verificação simplificada da flambagem por distorção"""
    # Esta é uma verificação simplificada - o cálculo completo seria mais complexo
    relacao_D_bw = D / bw
    relacao_bf_bw = bf / bw
    
    # Valores mínimos da relação D/bw (extraídos das tabelas no PDF)
    tabela_minimos = {
        (0.4, 25): 0.04,
        (0.6, 25): 0.06,
        # Adicionar mais valores conforme tabela completa
    }
    
    # Verificar se a relação D/bw atende aos mínimos para dispensar a verificação
    chave = (round(relacao_bf_bw,1), round(bw/t))
    if chave in tabela_minimos:
        if relacao_D_bw >= tabela_minimos[chave]:
            return True, "Dispensada (atende relação mínima D/bw)"
    
    return False, "Necessária verificação detalhada"

def gerar_relatorio_latex(dados):
    """Gera um relatório técnico em LaTeX com os resultados"""
    doc = Document('relatorio_dimensionamento')
    
    # Pré-ambulo do documento
    doc.preamble.append(Command('title', 'Relatório de Dimensionamento - NBR 14762:2001'))
    doc.preamble.append(Command('author', 'Streamlit App'))
    doc.preamble.append(Command('date', '\\today'))
    doc.append(Command('maketitle'))
    
    # Seção 1: Dados de entrada
    with doc.create(Section('Dados de Entrada')):
        doc.append('Propriedades do aço:\n')
        doc.append(Math(data=[r'f_y = ', f'{dados["fy"]}', r'\text{ MPa}']))
        doc.append('\n\n')
        
        doc.append('Propriedades geométricas do perfil:\n')
        with doc.create(Tabular('|l|c|')) as table:
            table.add_row(['Largura da mesa (bf)', f'{dados["bf"]} mm'])
            table.add_row(['Altura da alma (bw)', f'{dados["bw"]} mm'])
            table.add_row(['Enrijecimento (D)', f'{dados["D"]} mm'])
            table.add_row(['Espessura (t)', f'{dados["t"]} mm'])
    
    # Seção 2: Resultados
    with doc.create(Section('Resultados do Dimensionamento')):
        with doc.create(Subsection('Flambagem Global')):
            doc.append(f'Modo crítico de flambagem: {dados["modo_critico"]}\n\n')
            doc.append(Math(data=[
                r'N_e = \min(',
                f'N_{{ex}} = {dados["Nex"]:.2f}\ \text{{kN}}, ',
                f'N_{{ey}} = {dados["Ney"]:.2f}\ \text{{kN}}, ',
                f'N_{{et}} = {dados["Net"]:.2f}\ \text{{kN}}) = ',
                f'{dados["Ne"]:.2f}\ \text{{kN}}'
            ]))
            doc.append('\n\n')
            
            doc.append('Fator de redução:\n')
            doc.append(Math(data=[
                r'\lambda_0 = \sqrt{\frac{A_{ef}f_y}{N_e}} = ',
                f'{dados["lambda0"]:.3f}'
            ]))
            doc.append('\n')
            doc.append(Math(data=[
                r'\rho = \frac{1}{\phi + \sqrt{\phi^2 - \lambda_0^2}} = ',
                f'{dados["rho"]:.3f}'
            ]))
            doc.append('\n\n')
            
            doc.append('Resistência de cálculo:\n')
            doc.append(Math(data=[
                r'N_{c,Rd} = \frac{\rho A_{ef} f_y}{\gamma} = ',
                f'{dados["NcRd"]:.2f}\ \text{{kN}}'
            ]))
        
        with doc.create(Subsection('Flambagem por Distorção')):
            doc.append(dados["verif_distorcional"][1] + '\n\n')
            if not dados["verif_distorcional"][0]:
                doc.append(Math(data=[
                    r'N_{c,Rd,dist} = A f_y (1 - 0.25\lambda_{dist}^2)/\gamma = ',
                    f'{dados["NcRd_dist"]:.2f}\ \text{{kN}}'
                ]))
    
    # Seção 3: Verificações finais
    with doc.create(Section('Verificações Finais')):
        doc.append('Verificação da resistência:\n')
        doc.append(Math(data=[
            r'\frac{N_{c,Sd}}{N_{c,Rd}} = ',
            f'{dados["NcSd"]/dados["NcRd"]:.3f}',
            r'\leq 1.0 \quad',
            'OK' if dados["NcSd"]/dados["NcRd"] <= 1.0 else 'NÃO OK'
        ]))
    
    return doc

# Interface do Streamlit
with st.sidebar:
    st.header("Dados de Entrada")
    
    # Propriedades do aço
    st.subheader("Propriedades do Aço")
    fy = st.number_input("Tensão de escoamento (fy) [MPa]", value=250, min_value=100, max_value=500)
    E = st.number_input("Módulo de elasticidade (E) [MPa]", value=205000, min_value=100000, max_value=300000)
    G = 0.385 * E
    
    # Solicitações
    st.subheader("Solicitações")
    NcSd = st.number_input("Força normal de compressão (Nc,Sd) [kN]", value=35.4)
    MxSd = st.number_input("Momento fletor em x (Mx,Sd) [kN.m]", value=0.0)
    MySd = st.number_input("Momento fletor em y (My,Sd) [kN.m]", value=0.0)
    
    # Geometria do perfil
    st.subheader("Geometria do Perfil")
    bf = st.number_input("Largura da mesa (bf) [mm]", value=40)
    bw = st.number_input("Altura da alma (bw) [mm]", value=100)
    D = st.number_input("Enrijecimento (D) [mm]", value=25)
    t = st.number_input("Espessura (t) [mm]", value=2.65, min_value=0.5, max_value=10.0, step=0.1)
    rm = t * 1.5  # Raio interno padrão
    
    # Comprimentos de flambagem
    st.subheader("Comprimentos de Flambagem")
    Lx = st.number_input("Comprimento em x (Lx) [mm]", value=2500)
    Ly = st.number_input("Comprimento em y (Ly) [mm]", value=2500)
    Lt = st.number_input("Comprimento para torção (Lt) [mm]", value=2500)
    
    # Coeficientes de flambagem
    st.subheader("Coeficientes de Flambagem")
    Kx = st.number_input("Coeficiente Kx", value=1.0, min_value=0.5, max_value=2.0, step=0.1)
    Ky = st.number_input("Coeficiente Ky", value=1.0, min_value=0.5, max_value=2.0, step=0.1)
    Kt = st.number_input("Coeficiente Kt", value=1.0, min_value=0.5, max_value=2.0, step=0.1)

# Botão para realizar cálculos
if st.button("Realizar Dimensionamento"):
    # Calcular propriedades geométricas
    props = calcular_propriedades_geometricas(bf, bw, D, t, rm)
    
    # Cálculo das forças normais de flambagem elástica
    Nex = calcular_ne(E, props['Ix'], Kx, Lx) / 1000  # Convertendo para kN
    Ney = calcular_ne(E, props['Iy'], Ky, Ly) / 1000
    Net = calcular_net(E, props['Cw'], G, props['It'], Kt, Lt, props['r0']) / 1000
    
    # Força normal de flambagem elástica (menor valor)
    Ne = min(Nex, Ney, Net)
    
    # Determinar o modo crítico de flambagem
    if Ne == Nex:
        modo_critico = "Flambagem por flexão em x"
        alpha = 0.34  # Curva b (valor padrão para perfis U)
    elif Ne == Ney:
        modo_critico = "Flambagem por flexão em y"
        alpha = 0.34  # Curva b
    else:
        modo_critico = "Flambagem por torção/flexo-torção"
        alpha = 0.34  # Curva b para torção/flexo-torção
    
    # Cálculo inicial do fator de redução (com Aef = A)
    lambda0 = calcular_lambda0(props['A'], fy, Ne)
    rho = calcular_fator_reducao(lambda0, alpha)
    
    # Tensão para cálculo das larguras efetivas
    sigma = rho * fy
    
    # Cálculo das larguras efetivas (simplificado)
    # Na prática, seria necessário calcular para cada elemento do perfil
    Aef = props['A']  # Simplificação - cálculo completo seria mais complexo
    
    # Cálculo final do fator de redução
    lambda0_final = calcular_lambda0(Aef, fy, Ne)
    rho_final = calcular_fator_reducao(lambda0_final, alpha)
    
    # Resistência de cálculo à compressão
    gamma = 1.1  # Coeficiente de ponderação da resistência
    NcRd = rho_final * Aef * fy / gamma / 1000  # Convertendo para kN
    
    # Verificação da flambagem por distorção
    verif_distorcional = verificar_flambagem_distorcional(bf, bw, D, t, fy, E)
    
    # Se necessário calcular a resistência à distorção
    if not verif_distorcional[0]:
        # Cálculo simplificado da resistência à distorção
        NcRd_dist = props['A'] * fy * (1 - 0.25) / gamma / 1000  # Exemplo simplificado
    else:
        NcRd_dist = float('inf')
    
    # Preparar dados para o relatório
    dados_relatorio = {
        'fy': fy,
        'E': E,
        'bf': bf,
        'bw': bw,
        'D': D,
        't': t,
        'NcSd': NcSd,
        'modo_critico': modo_critico,
        'Nex': Nex,
        'Ney': Ney,
        'Net': Net,
        'Ne': Ne,
        'lambda0': lambda0_final,
        'rho': rho_final,
        'NcRd': NcRd,
        'verif_distorcional': verif_distorcional,
        'NcRd_dist': NcRd_dist if not verif_distorcional[0] else float('inf')
    }
    
    # Gerar relatório LaTeX
    doc = gerar_relatorio_latex(dados_relatorio)
    
    # Mostrar resultados na interface
    st.header("Resultados do Dimensionamento")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Propriedades Geométricas")
        st.write(f"Área bruta (A): {props['A']:.2f} mm²")
        st.write(f"Ix: {props['Ix']:.2f} mm⁴")
        st.write(f"Iy: {props['Iy']:.2f} mm⁴")
        st.write(f"It: {props['It']:.2f} mm⁴")
        st.write(f"rx: {props['rx']:.2f} mm")
        st.write(f"ry: {props['ry']:.2f} mm")
        
        st.subheader("Flambagem Global")
        st.write(f"Modo crítico: {modo_critico}")
        st.write(f"Nex: {Nex:.2f} kN")
        st.write(f"Ney: {Ney:.2f} kN")
        st.write(f"Net: {Net:.2f} kN")
        st.write(f"Ne (valor crítico): {Ne:.2f} kN")
        st.write(f"λ₀: {lambda0_final:.3f}")
        st.write(f"ρ: {rho_final:.3f}")
        st.write(f"Nc,Rd: {NcRd:.2f} kN")
    
    with col2:
        st.subheader("Verificações")
        st.write(f"Flambagem por distorção: {verif_distorcional[1]}")
        if not verif_distorcional[0]:
            st.write(f"Nc,Rd,dist: {NcRd_dist:.2f} kN")
        
        st.subheader("Verificação Final")
        relacao = NcSd / NcRd
        st.write(f"Nc,Sd / Nc,Rd = {relacao:.3f}")
        if relacao <= 1.0:
            st.success("Perfil VERIFICADO com sucesso!")
        else:
            st.error("Perfil NÃO VERIFICADO! A resistência é insuficiente.")
        
        # Visualização do perfil
        fig, ax = plt.subplots(figsize=(6, 6))
        # Desenho simplificado do perfil U
        points = [
            [0, 0], [bf, 0], [bf, t], [t, t], 
            [t, bw-t], [bf, bw-t], [bf, bw], [0, bw]
        ]
        points = np.array(points)
        ax.plot(points[:,0], points[:,1], 'b-', linewidth=2)
        ax.set_aspect('equal')
        ax.set_title("Geometria do Perfil")
        st.pyplot(fig)
    
    # Gerar e disponibilizar relatório LaTeX
    st.header("Relatório Técnico")
    
    with tempfile.NamedTemporaryFile(suffix=".tex", delete=False) as tmp:
        doc.generate_tex(tmp.name)
        tmp.seek(0)
        latex_content = tmp.read().decode('utf-8')
    
    st.download_button(
        label="Baixar Relatório LaTeX",
        data=latex_content,
        file_name="relatorio_dimensionamento.tex",
        mime="text/plain"
    )
    
    st.subheader("Pré-visualização do LaTeX")
    st.code(latex_content, language='tex')
