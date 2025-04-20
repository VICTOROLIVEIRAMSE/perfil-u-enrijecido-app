import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt

# Configuração do tema Dracula
def setup_theme():
    st.markdown("""
    <style>
        :root {
            --primary: #ff79c6;
            --background: #282a36;
            --secondary: #bd93f9;
            --text: #f8f8f2;
            --accent: #50fa7b;
        }
        .stApp {
            background-color: var(--background);
            color: var(--text);
        }
        .stButton>button {
            background-color: var(--secondary);
            color: #282a36;
            font-weight: bold;
        }
        .metric {
            background-color: #44475a;
            border-left: 4px solid var(--secondary);
        }
    </style>
    """, unsafe_allow_html=True)

def calcular_propriedades(largura, altura, espessura, raio, labio):
    """Calcula as propriedades geométricas do perfil U enrijecido"""
    # Cálculos básicos
    area_total = 2*(labio*espessura) + (largura - 2*raio - 2*labio)*espessura + 2*(altura - 2*raio)*espessura
    area_total += 4*(math.pi*(raio + espessura/2)*espessura)  # Curvas
    
    # Centroide (simplificado)
    xg = largura/2  # Considerando simetria
    yg = altura/2
    
    # Momento de inércia (aproximado)
    Ix = (largura * altura**3)/12 - ((largura - 2*espessura)*(altura - 2*espessura)**3)/12
    Iy = (altura * largura**3)/12 - ((altura - 2*espessura)*(largura - 2*espessura)**3)/12
    
    return {
        'Área (mm²)': round(area_total, 2),
        'Ix (mm⁴)': round(Ix, 2),
        'Iy (mm⁴)': round(Iy, 2),
        'Wx (mm³)': round(Ix/(altura/2), 2),
        'Wy (mm³)': round(Iy/(largura/2), 2)
    }

def plot_perfil(largura, altura, espessura):
    """Cria uma visualização gráfica do perfil"""
    fig, ax = plt.subplots(figsize=(8, 4))
    
    # Coordenadas do perfil U
    pontos = np.array([
        [0, 0],
        [largura, 0],
        [largura, -altura],
        [0, -altura],
        [0, -altura+espessura],
        [largura-espessura, -altura+espessura],
        [largura-espessura, -espessura],
        [espessura, -espessura],
        [espessura, -altura+espessura],
        [0, -altura+espessura]
    ])
    
    ax.plot(pontos[:,0], pontos[:,1], color='#bd93f9', linewidth=2)
    ax.fill(pontos[:,0], pontos[:,1], color='#44475a', alpha=0.3)
    ax.set_aspect('equal')
    ax.grid(True, color='#6272a4', linestyle='--', alpha=0.3)
    ax.set_facecolor('#282a36')
    fig.patch.set_facecolor('#282a36')
    ax.spines[:].set_color('#f8f8f2')
    ax.tick_params(colors='#f8f8f2')
    
    return fig

def main():
    setup_theme()
    
    st.title("Perfil U Enrijecido - NBR 14762")
    st.markdown("### Dimensionamento de perfis formados a frio")
    
    with st.sidebar:
        st.header("Dimensões do Perfil")
        largura = st.slider("Largura (mm)", 50, 300, 100)
        altura = st.slider("Altura (mm)", 30, 200, 50)
        espessura = st.slider("Espessura (mm)", 0.5, 5.0, 1.5, 0.1)
        raio = st.slider("Raio (mm)", 1.0, 10.0, 3.0, 0.5)
        labio = st.slider("Lábio (mm)", 5, 50, 15)
    
    # Cálculos e resultados
    props = calcular_propriedades(largura, altura, espessura, raio, labio)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Área da Seção", f"{props['Área (mm²)']} mm²")
        st.metric("Mom. Inércia X", f"{props['Ix (mm⁴)']} mm⁴")
    
    with col2:
        st.metric("Mom. Inércia Y", f"{props['Iy (mm⁴)']} mm⁴")
        st.metric("Mód. Resistente", f"{props['Wx (mm³)']} mm³")
    
    # Visualização gráfica
    st.pyplot(plot_perfil(largura, altura, espessura))

if __name__ == "__main__":
    main()
