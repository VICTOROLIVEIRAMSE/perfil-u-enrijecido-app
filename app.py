# Este é um esboço funcional do app para verificar perfil U enrijecido.
# Ele depende do Streamlit, que deve ser instalado no ambiente com: pip install streamlit

try:
    import streamlit as st
    import numpy as np
    import matplotlib.pyplot as plt
    import os
except ModuleNotFoundError as e:
    print("Erro ao importar bibliotecas. Certifique-se de que o ambiente possui streamlit, numpy e matplotlib instalados.")
    raise e

# Configuração da página
st.set_page_config(page_title="Verificador de Perfil U Enrijecido", layout="centered")
st.title("Verificador de Perfil U Enrijecido")
st.markdown("""
<style>
    .main {background-color: #f5f7fa;}
    .stButton>button {border-radius: 12px; background-color: #4a90e2; color: white;}
    .stTextInput>div>div>input {border-radius: 8px;}
</style>
""", unsafe_allow_html=True)

st.subheader("Parâmetros do Perfil")
altura = st.number_input("Altura da alma (mm)", value=150.0)
largura = st.number_input("Largura da aba (mm)", value=50.0)
espessura = st.number_input("Espessura (mm)", value=2.0)
comprimento = st.number_input("Comprimento total (mm)", value=2000.0)
fy = st.selectbox("Resistência do Aço fy (MPa)", [230, 300, 350, 420], index=2)

st.subheader("Parâmetros de Flambagem")
k = st.slider("Coeficiente de comprimento efetivo (K)", 0.5, 2.0, value=1.0)
le = comprimento * k

# Cálculo da área e módulo de inércia aproximado (simplificado para perfil U dobrado)
b = largura / 1000
h = altura / 1000
t = espessura / 1000

area = 2 * b * t + h * t  # em m²
ix = ((b * h**3) / 12) - (((b - t) * (h - 2*t)**3) / 12)  # m^4, simplificação

# Cálculo da carga crítica de Euler
E = 200_000  # MPa
pi = np.pi
Pcr = (pi**2 * E * ix) / ((le / 1000)**2)  # kN

# Tensão de flambagem crítica
fcr = (Pcr * 1000) / area / 1e6  # MPa

# Gráfico de capacidade x comprimento
comprimentos = np.linspace(500, 6000, 100)
le_array = comprimentos * k
Pcr_array = (pi**2 * E * ix) / ((le_array / 1000)**2)

st.subheader("Gráfico: Capacidade de Carga x Comprimento")
fig, ax = plt.subplots()
ax.plot(comprimentos, Pcr_array, label="Carga Crítica (N)", color="#4a90e2")
ax.axhline(y=fy*area*1e6, color='red', linestyle='--', label="Limite de Escoamento")
ax.set_xlabel("Comprimento (mm)")
ax.set_ylabel("Carga Crítica (N)")
ax.legend()
ax.grid(True)
st.pyplot(fig)

# Relatório LaTeX
if st.button("Gerar LaTeX"):
    latex_code = f"""
\\documentclass[12pt]{{article}}
\\usepackage{{amsmath,graphicx}}
\\title{{Relatório de Verificação do Perfil U Enrijecido}}
\\begin{{document}}
\\maketitle
\\section*{{Dados de Entrada}}
\\begin{{itemize}}
  \item Altura da alma: {altura} mm
  \item Largura da aba: {largura} mm
  \item Espessura: {espessura} mm
  \item Comprimento: {comprimento} mm
  \item Resistência do aço: {fy} MPa
  \item Coeficiente K: {k}
\\end{{itemize}}

\\section*{{Resultados}}
\\begin{{itemize}}
  \item Área: {area*1e6:.2f} mm$^2$
  \item Módulo de inércia (aprox.): {ix*1e12:.2f} mm$^4$
  \item Comprimento efetivo: {le:.1f} mm
  \item Carga crítica de flambagem: {Pcr:.2f} N
  \item Tensão crítica de flambagem: {fcr:.2f} MPa
\\end{{itemize}}
\\end{{document}}
"""
    st.code(latex_code, language="latex")

    tex_filename = "relatorio_perfil_U_enrijecido.tex"
    with open(tex_filename, "w", encoding="utf-8") as f:
        f.write(latex_code)
    st.success(f"Arquivo LaTeX salvo como {tex_filename}")
