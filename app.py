import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tempfile
from pylatex import Document, Section, Subsection, Math, Tabular, Command
from pylatex.utils import italic, bold

# Configuração inicial do Streamlit
st.set_page_config(page_title="Dimensionamento de Perfis Metálicos", layout="wide")
st.title("Dimensionamento de Perfis Metálicos - NBR 14762:2001")

# Função para verificar instalações de pacotes
def verificar_instalacoes():
    required_packages = ['numpy', 'pandas', 'matplotlib', 'pylatex']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        st.warning(f"Pacotes faltando: {', '.join(missing_packages)}")
        if st.button("Instalar pacotes automaticamente"):
            import subprocess
            import sys
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", *missing_packages])
                st.success("Pacotes instalados com sucesso! Por favor, recarregue a página.")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Erro na instalação: {str(e)}")
        return False
    return True

# Funções de cálculo
def calcular_propriedades_geometricas(bf, bw, D, t, rm):
    """Calcula propriedades geométricas do perfil U enrijecido"""
    try:
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
    except Exception as e:
        st.error(f"Erro no cálculo das propriedades geométricas: {str(e)}")
        return None

# ... (outras funções de cálculo aqui - manter a mesma estrutura com tratamento de erros)

# Interface principal
if verificar_instalacoes():
    with st.sidebar:
        st.header("Dados de Entrada")
        
        # Propriedades do aço
        st.subheader("Propriedades do Aço")
        fy = st.number_input("Tensão de escoamento (fy) [MPa]", value=250)
        E = st.number_input("Módulo de elasticidade (E) [MPa]", value=205000)
        
        # Solicitações
        st.subheader("Solicitações")
        NcSd = st.number_input("Força normal de compressão (Nc,Sd) [kN]", value=35.4)
        
        # Geometria do perfil
        st.subheader("Geometria do Perfil")
        bf = st.number_input("Largura da mesa (bf) [mm]", value=40)
        bw = st.number_input("Altura da alma (bw) [mm]", value=100)
        D = st.number_input("Enrijecimento (D) [mm]", value=25)
        t = st.number_input("Espessura (t) [mm]", value=2.65, min_value=0.5, step=0.1)

    if st.button("Realizar Dimensionamento"):
        try:
            # Cálculos principais
            props = calcular_propriedades_geometricas(bf, bw, D, t, t*1.5)
            if props is None:
                st.stop()
            
            # Exibir resultados
            st.header("Resultados")
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Propriedades Geométricas")
                st.write(f"Área bruta (A): {props['A']:.2f} mm²")
                st.write(f"Ix: {props['Ix']:.2f} mm⁴")
                st.write(f"Iy: {props['Iy']:.2f} mm⁴")
            
            with col2:
                # Visualização do perfil
                fig, ax = plt.subplots()
                # Código para desenhar o perfil...
                st.pyplot(fig)
                
        except Exception as e:
            st.error(f"Erro durante o dimensionamento: {str(e)}")
