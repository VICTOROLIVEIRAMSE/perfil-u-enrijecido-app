import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from io import StringIO
import tempfile
import os
from pylatex import Document, Section, Subsection, Math, Tabular, Figure, Command
from pylatex.utils import italic, bold

# Configuração inicial do Streamlit
st.set_page_config(page_title="Dimensionamento de Perfis Metálicos", layout="wide")
st.title("Dimensionamento de Perfis Metálicos - NBR 14762:2001")

# Funções de cálculo
def calcular_propriedades_geometricas(bf, bw, D, t, rm):
    A = t * (2*bf + bw + 2*D)
    Ix = (t * (2*bf**3 + bw**3 + 6*bf*bw**2 + 6*bf*D**2)) / 12
    Iy = (t * (2*bf**3 + 6*bf*bw**2 + 6*bf*D**2)) / 12
    It = (t**3 * (2*bf + bw + 2*D)) / 3
    Cw = (bf**2 * bw**2 * t) / 24
    rx = np.sqrt(Ix/A)
    ry = np.sqrt(Iy/A)
    x0 = bf/2 + t/2
    y0 = 0
    r0 = np.sqrt(rx**2 + ry**2 + x0**2 + y0**2)
    return {
        'A': A, 'Ix': Ix, 'Iy': Iy, 'It': It, 'Cw': Cw,
        'rx': rx, 'ry': ry, 'x0': x0, 'y0': y0, 'r0': r0
    }

def calcular_ne(E, I, K, L):
    return (np.pi**2 * E * I) / (K * L)**2

def calcular_net(E, Cw, G, It, Kt, Lt, r0):
    return (1/r0**2) * ((np.pi**2 * E * Cw)/(Kt * Lt)**2 + G * It)

def calcular_lambda0(Aef, fy, Ne):
    return np.sqrt(Aef * fy / Ne)

def calcular_fator_reducao(l0, alpha):
    beta = 0.5 * (1 + alpha * (l0 - 0.2) + l0**2)
    rho = 1 / (beta + np.sqrt(beta**2 - l0**2))
    return min(rho, 1.0)

def verificar_flambagem_distorcional(bf, bw, D, t, fy, E):
    relacao_D_bw = D / bw
    relacao_bf_bw = bf / bw
    if relacao_D_bw >= 0.04 and relacao_bf_bw <= 1.0:
        return True, "Dispensada (atende relação mínima D/bw)"
    return False, "Necessária verificação detalhada"

def gerar_relatorio_latex(dados):
    doc = Document('relatorio_dimensionamento')
    doc.preamble.append(Command('title', 'Relatório de Dimensionamento - NBR 14762:2001'))
    doc.preamble.append(Command('author', 'Streamlit App'))
    doc.preamble.append(Command('date', '\\today'))
    doc.append(Command('maketitle'))
    with doc.create(Section('Dados de Entrada')):
        with doc.create(Tabular('|l|c|')) as table:
            table.add_row(['fy (MPa)', dados['fy']])
            table.add_row(['E (MPa)', dados['E']])
            table.add_row(['bf (mm)', dados['bf']])
            table.add_row(['bw (mm)', dados['bw']])
            table.add_row(['D (mm)', dados['D']])
            table.add_row(['t (mm)', dados['t']])
    with doc.create(Section('Resultados')):
        with doc.create(Subsection('Flambagem')):
            doc.append(Math(data=[f'N_{{ex}} = {dados["Nex"]:.2f}\ \text{{kN}}']))
            doc.append(Math(data=[f'N_{{ey}} = {dados["Ney"]:.2f}\ \text{{kN}}']))
            doc.append(Math(data=[f'N_{{et}} = {dados["Net"]:.2f}\ \text{{kN}}']))
            doc.append(Math(data=[f'N_e = {dados["Ne"]:.2f}\ \text{{kN}}']))
            doc.append(Math(data=[f'\\lambda_0 = {dados["lambda0"]:.3f}']))
            doc.append(Math(data=[f'\\rho = {dados["rho"]:.3f}']))
            doc.append(Math(data=[f'N_{{c,Rd}} = {dados["NcRd"]:.2f}\ \text{{kN}}']))
        with doc.create(Subsection('Verificação')):
            doc.append(f"{dados['verif_distorcional'][1]}")
            if not dados['verif_distorcional'][0]:
                doc.append(Math(data=[f'N_{{c,Rd,dist}} = {dados["NcRd_dist"]:.2f}\ \text{{kN}}']))
            doc.append(Math(data=[f'\\frac{{N_{{c,Sd}}}}{{N_{{c,Rd}}}} = {dados["NcSd"]/dados["NcRd"]:.3f}']))
    return doc

# Interface do Streamlit
st.sidebar.header("Entrada de Dados")
fy = st.sidebar.number_input("Tensão de escoamento fy [MPa]", value=250)
E = st.sidebar.number_input("Módulo de Elasticidade E [MPa]", value=205000)
G = 0.385 * E
NcSd = st.sidebar.number_input("Força de compressão Nc,Sd [kN]", value=35.4)
bf = st.sidebar.number_input("Largura da mesa bf [mm]", value=40)
bw = st.sidebar.number_input("Altura da alma bw [mm]", value=100)
D = st.sidebar.number_input("Enrijecimento D [mm]", value=25)
t = st.sidebar.number_input("Espessura t [mm]", value=2.65)
rm = 1.5 * t
L = st.sidebar.number_input("Comprimento do elemento [mm]", value=2500)
K = st.sidebar.number_input("Coeficiente de flambagem K", value=1.0)
Lt = st.sidebar.number_input("Comprimento para torção Lt [mm]", value=2500)
Kt = st.sidebar.number_input("Coeficiente para torção Kt", value=1.0)
gamma = 1.1

if st.button("Calcular Dimensionamento"):
    props = calcular_propriedades_geometricas(bf, bw, D, t, rm)
    Aef = props['A']
    Nex = calcular_ne(E, props['Ix'], K, L)
    Ney = calcular_ne(E, props['Iy'], K, L)
    Net = calcular_net(E, props['Cw'], G, props['It'], Kt, Lt, props['r0'])
    Ne = min(Nex, Ney, Net)
    modo_critico = 'flexão-x' if Ne == Nex else ('flexão-y' if Ne == Ney else 'torção')
    lambda0 = calcular_lambda0(Aef, fy, Ne)
    rho = calcular_fator_reducao(lambda0, alpha=0.34)
    NcRd = (rho * Aef * fy) / gamma / 1000
    verif_distorcional = verificar_flambagem_distorcional(bf, bw, D, t, fy, E)
    NcRd_dist = Aef * fy * (1 - 0.25) / gamma / 1000 if not verif_distorcional[0] else float('inf')
    dados = {
        'fy': fy, 'E': E, 'G': G,
        'bf': bf, 'bw': bw, 'D': D, 't': t,
        'Aef': Aef, 'Nex': Nex/1000, 'Ney': Ney/1000, 'Net': Net/1000, 'Ne': Ne/1000,
        'modo_critico': modo_critico,
        'lambda0': lambda0, 'rho': rho,
        'NcRd': NcRd, 'NcSd': NcSd,
        'verif_distorcional': verif_distorcional,
        'NcRd_dist': NcRd_dist
    }
    st.subheader("Resultados")
    st.write(f"**Modo Crítico:** {modo_critico}")
    st.write(f"**Nex:** {dados['Nex']:.2f} kN | Ney: {dados['Ney']:.2f} kN | Net: {dados['Net']:.2f} kN")
    st.write(f"**Ne:** {dados['Ne']:.2f} kN")
    st.write(f"**λ₀:** {lambda0:.3f} | **ρ:** {rho:.3f}")
    st.write(f"**Nc,Rd:** {NcRd:.2f} kN")
    st.write(f"**Verificação Final:** NcSd / NcRd = {NcSd/NcRd:.3f} {'✅ OK' if NcSd/NcRd <= 1.0 else '❌ NÃO OK'}")

    if not verif_distorcional[0]:
        st.write(f"**Nc,Rd,dist:** {NcRd_dist:.2f} kN")

    doc = gerar_relatorio_latex(dados)
    with tempfile.TemporaryDirectory() as tmp:
        tex_path = os.path.join(tmp, 'relatorio')
        doc.generate_pdf(tex_path, clean_tex=False)
        pdf_path = tex_path + '.pdf'
        with open(pdf_path, 'rb') as f:
            st.download_button(
                label="📄 Baixar Relatório em PDF",
                data=f,
                file_name="relatorio_dimensionamento.pdf",
                mime="application/pdf"
            )
