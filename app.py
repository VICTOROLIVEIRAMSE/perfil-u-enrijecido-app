import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO
import tempfile
import os
import sys
from pylatex import Document, Section, Subsection, Math, Tabular, Figure, Command
from pylatex.utils import italic, bold

# Verificar e instalar pacotes necessários
try:
    from pylatex import Document, Section, Subsection, Math, Tabular, Figure, Command
except ImportError:
    st.error("Algumas bibliotecas necessárias não estão instaladas. Instalando agora...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pylatex", "matplotlib"])
    from pylatex import Document, Section, Subsection, Math, Tabular, Figure, Command

# Configuração inicial do Streamlit
st.set_page_config(page_title="Dimensionamento de Perfis Metálicos", layout="wide")
st.title("Dimensionamento de Perfis Metálicos - NBR 14762:2001")

# Funções de cálculo (mantidas as mesmas do código anterior)
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

# ... (manter todas as outras funções de cálculo do código anterior)

# Adicionar esta nova função para verificar instalações
def verificar_instalacoes():
    """Verifica se todos os pacotes necessários estão instalados"""
    pacotes_necessarios = ['numpy', 'pandas', 'matplotlib', 'pylatex']
    faltando = []
    
    for pacote in pacotes_necessarios:
        try:
            __import__(pacote)
        except ImportError:
            faltando.append(pacote)
    
    if faltando:
        st.warning(f"Os seguintes pacotes estão faltando: {', '.join(faltando)}")
        if st.button("Instalar pacotes faltantes automaticamente"):
            import subprocess
            import sys
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", *faltando])
                st.success("Pacotes instalados com sucesso! Por favor, recarregue a página.")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Erro ao instalar pacotes: {e}")
        return False
    return True

# Interface principal só executa se todos os pacotes estiverem instalados
if verificar_instalacoes():
    with st.sidebar:
        st.header("Dados de Entrada")
        
        # ... (manter todo o restante da interface do código anterior)

    # Botão para realizar cálculos
    if st.button("Realizar Dimensionamento"):
        try:
            # ... (manter todo o restante da lógica de cálculo do código anterior)
            
        except Exception as e:
            st.error(f"Ocorreu um erro durante os cálculos: {str(e)}")
            st.info("Por favor, verifique os dados de entrada e tente novamente.")
