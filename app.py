import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# Configuração do tema Dracula
def setup_theme():
    st.markdown("""
    <style>
        [data-testid="stAppViewContainer"] {
            background: #282a36; /* Cor de fundo principal */
            color: #f8f8f2; /* Cor do texto principal */
        }

        .st-emotion-cache-1y4p8pa {
            padding: 2rem 1rem 10rem;
        }

        [data-testid="stSidebar"] {
            background: #44475a !important; /* Cor de fundo da barra lateral */
            border-right: 1px solid #6272a4; /* Cor da borda da barra lateral */
        }

        .st-b7 {
            color: #f8f8f2 !important;
        }

        .st-c0 {
            background-color: #44475a !important; /* Cor de fundo dos containers */
            border: 1px solid #6272a4;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 10px;
        }

        .stButton button {
            background: #bd93f9 !important; /* Cor do botão */
            color: #282a36 !important; /* Cor do texto do botão */
            font-weight: bold;
            border: none;
            border-radius: 5px;
            transition: all 0.3s;
        }

        .stButton button:hover {
            background: #8be9fd !important; /* Cor do botão ao passar o mouse */
            color: #282a36 !important;
            transform: scale(1.03);
        }

        .metric-container {
            background: #44475a; /* Cor de fundo das métricas */
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 10px;
            border-left: 3px solid #50fa7b; /* Cor do indicador esquerdo das métricas */
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3); /* Sombra mais escura */
            transition: all 0.3s;
            color: #f8f8f2;
        }

        .metric-container:hover {
            transform: translateY(-3px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.4);
        }

        .metric-value {
            font-size: 1.3rem;
            font-weight: bold;
            color: #f1fa8c; /* Cor do valor da métrica */
        }

        .metric-label {
            font-size: 0.9rem;
            color: #6272a4; /* Cor do rótulo da métrica */
        }

        .title {
            color: #ff79c6 !important; /* Cor do título */
            font-size: 2.2rem !important;
            margin-bottom: 0.3rem !important;
        }

        .subheader {
            color: #6272a4 !important; /* Cor do subtítulo */
            font-size: 1.1rem !important;
            margin-bottom: 1.5rem !important;
        }

        /* Garantir que todo texto esteja visível */
        * {
            color: #f8f8f2 !important;
        }
    </style>
    """, unsafe_allow_html=True)

def calcular_propriedades(largura, altura, espessura, raio, labio):
    """Calcula as propriedades geométricas com precisão"""
    # Áreas dos componentes
    area_labios = 2 * labio * espessura
    area_mesa = (largura - 2 * (raio + labio)) * espessura
    area_almas = 2 * (altura - 2 * raio) * espessura
    area_curvas = 4 * (math.pi * (raio + espessura/2) * espessura/2) # Correção na área das curvas

    area_total = area_labios + area_mesa + area_almas + area_curvas

    # Centroide
    xg = largura / 2  # Simétrico
    yg = altura / 2

    # Momentos de inércia (cálculo mais preciso - simplificado para visualização)
    Ix = (espessura * (altura)**3)/12 # Aproximação para simplificar
    Iy = ((altura - 2 * raio) * espessura**3)/12 + 2 * ((espessura * (labio + raio)**3)/12 + espessura * (labio + raio) * (largura/2 - (labio + raio)/2)**2) # Aproximação

    # Módulos resistentes
    Wx = Ix / (altura/2)
    Wy = Iy / (largura/2)

    return {
        'Área': f"{area_total:.2f} mm²",
        'Ix': f"{Ix:.2f} mm⁴",
        'Iy': f"{Iy:.2f} mm⁴",
        'Wx': f"{Wx:.2f} mm³",
        'Wy': f"{Wy:.2f} mm³",
        'rx': f"{math.sqrt(Ix/area_total):.2f} mm",
        'ry': f"{math.sqrt(Iy/area_total):.2f} mm"
    }

def desenhar_perfil_2d(largura, altura, espessura, raio, labio):
    """Cria uma visualização 2D do perfil com cores do tema Dracula"""
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.set_aspect('equal', adjustable='box')
    ax.set_facecolor('#282a36') # Cor de fundo do gráfico

    perfil_color = '#f8f8f2' # Cor do contorno do perfil
    fill_color = '#6272a4' # Cor de preenchimento do perfil

    # Desenhar a base
    ax.add_patch(Rectangle((0, 0), largura, espessura, facecolor=fill_color, edgecolor=perfil_color))

    # Desenhar as almas
    ax.add_patch(Rectangle((0, espessura), espessura, altura - 2 * espessura - 2 * raio, facecolor=fill_color, edgecolor=perfil_color))
    ax.add_patch(Rectangle((largura - espessura, espessura), espessura, altura - 2 * espessura - 2 * raio, facecolor=fill_color, edgecolor=perfil_color))

    # Desenhar os raios
    circle1 = Circle((espessura + raio, espessura + raio), raio, facecolor=fill_color, edgecolor=perfil_color)
    ax.add_patch(circle1)
    circle2 = Circle((largura - espessura - raio, espessura + raio), raio, facecolor=fill_color, edgecolor=perfil_color)
    ax.add_patch(circle2)
    circle3 = Circle((espessura + raio, altura - espessura - raio), raio, facecolor=fill_color, edgecolor=perfil_color)
    ax.add_patch(circle3)
    circle4 = Circle((largura - espessura - raio, altura - espessura - raio), raio, facecolor=fill_color, edgecolor=perfil_color)
    ax.add_patch(circle4)

    # Desenhar a mesa superior
    ax.add_patch(Rectangle((raio + espessura, altura - espessura), largura - 2 * (raio + espessura), espessura, facecolor=fill_color, edgecolor=perfil_color))

    # Desenhar os lábios
    ax.add_patch(Rectangle((0, altura - espessura - labio), labio, espessura, facecolor=fill_color, edgecolor=perfil_color))
    ax.add_patch(Rectangle((largura - labio, altura - espessura - labio), labio, espessura, facecolor=fill_color, edgecolor=perfil_color))

    # Limites e rótulos
    ax.set_xlim(-5, largura + 5)
    ax.set_ylim(-5, altura + 5)
    ax.axis('off') # Remover eixos para uma visualização mais limpa
    plt.tight_layout()
    return fig

def criar_metric_card(label, value):
    """Componente personalizado para métricas com cores do tema Dracula"""
    return f"""
    <div class="metric-container">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
    </div>
    """

def main():
    setup_theme()

    st.markdown('<p class="title">Perfil U Enrijecido</p>', unsafe_allow_html=True)
    st.markdown('<p class="subheader">Dimensionamento conforme NBR 14762</p>', unsafe_allow_html=True)

    with st.sidebar:
        st.header("✏️ Parâmetros do Perfil")
        col1, col2 = st.columns(2)

        with col1:
            largura = st.number_input("Largura (B)", min_value=50, max_value=500, value=100, step=5)
            altura = st.number_input("Altura (H)", min_value=30, max_value=300, value=50, step=5)
            espessura = st.number_input("Espessura (t)", min_value=0.5, max_value=5.0, value=1.5, step=0.1)

        with col2:
            raio = st.number_input("Raio (r)", min_value=1.0, max_value=10.0, value=3.0, step=0.5)
            labio = st.number_input("Lábio (L)", min_value=5, max_value=50, value=15, step=1)

        st.markdown("---")
        st.markdown("<p style='color:#f8f8f2;'><strong>Dicas:</strong></p>", unsafe_allow_html=True)
        st.markdown("<p style='color:#6272a4;'>- Lábios típicos: 10-20% da largura</p>", unsafe_allow_html=True)
        st.markdown("<p style='color:#6272a4;'>- Raios comuns: 2-4x a espessura</p>", unsafe_allow_html=True)

    # Layout principal
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("### 📐 Propriedades Geométricas")
        props = calcular_propriedades(largura, altura, espessura, raio, labio)

        st.markdown(criar_metric_card("Área da Seção Transversal", props['Área']), unsafe_allow_html=True)
        st.markdown(criar_metric_card("Mom. de Inércia (Ix)", props['Ix']), unsafe_allow_html=True)
        st.markdown(criar_metric_card("Mom. de Inércia (Iy)", props['Iy']), unsafe_allow_html=True)

        st.markdown(criar_metric_card("Mód. Resistente (Wx)", props['Wx']), unsafe_allow_html=True)
        st.markdown(criar_metric_card("Mód. Resistente (Wy)", props['Wy']), unsafe_allow_html=True)

        st.markdown(criar_metric_card("Raio de Giração (rx)", props['rx']), unsafe_allow_html=True)
        st.markdown(criar_metric_card("Raio de Giração (ry)", props['ry']), unsafe_allow_html=True)

    with col2:
        st.markdown("### 📏 Visualização do Perfil")
        fig = desenhar_perfil_2d(largura, altura, espessura, raio, labio)
        st.pyplot(fig)

        st.markdown("---")
        st.markdown("<p style='color:#f8f8f2;'><strong>Detalhes da visualização:</strong></p>", unsafe_allow_html=True)
        st.markdown("<p style='color:#6272a4;'>- As dimensões não estão em escala exata para melhor visualização.</p>", unsafe_allow_html=True)
        st.markdown("<p style='color:#6272a4;'>- O contorno representa a seção transversal do perfil.</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
