import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Arc

# Configuração do tema Dracula (cores vibrantes ajustadas)
def setup_theme():
    st.markdown("""
    <style>
        [data-testid="stAppViewContainer"] {
            background: #282a36;
            color: #f8f8f2;
        }

        .st-emotion-cache-1y4p8pa {
            padding: 2rem 1rem 3rem;
        }

        [data-testid="stSidebar"] {
            background: #44475a !important;
            border-right: 1px solid #6272a4;
            padding-top: 2rem !important;
        }

        .st-b7 {
            color: #f8f8f2 !important;
        }

        .st-c0 {
            background-color: #44475a !important;
            border: 1px solid #6272a4;
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1.2rem;
        }

        .stButton button {
            background: #bd93f9 !important;
            color: #282a36 !important;
            font-weight: 500;
            border: none;
            border-radius: 8px;
            transition: all 0.3s;
            padding: 0.75rem 1.5rem;
        }

        .stButton button:hover {
            background: #8be9fd !important;
            color: #282a36 !important;
            transform: scale(1.02);
        }

        .metric-container {
            background: #44475a;
            border-radius: 8px;
            padding: 1.2rem;
            margin-bottom: 1rem;
            border-left: 5px solid #50fa7b;
            box-shadow: 0 3px 6px rgba(0, 0, 0, 0.3);
            transition: all 0.3s;
            color: #f8f8f2;
        }

        .metric-container:hover {
            transform: translateY(-0.25rem);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.4);
        }

        .metric-value {
            font-size: 1.5rem;
            font-weight: 600;
            color: #f1fa8c; /* Amarelo vibrante */
            margin-bottom: 0.2rem;
        }

        .metric-label {
            font-size: 0.95rem;
            color: #f8f8f2;
            opacity: 0.8;
        }

        .title {
            color: #ff79c6 !important; /* Rosa vibrante */
            font-size: 2.5rem !important;
            margin-bottom: 0.5rem !important;
            font-weight: 700;
        }

        .subheader {
            color: #6272a4 !important;
            font-size: 1.2rem !important;
            margin-bottom: 1.8rem !important;
            font-weight: 400;
        }

        h3 {
            color: #f8f8f2;
            font-size: 1.4rem;
            margin-bottom: 1rem;
        }

        .streamlit-expander {
            background-color: #44475a !important;
            border: 1px solid #6272a4 !important;
            border-radius: 8px !important;
            margin-bottom: 1rem !important;
        }

        .streamlit-expander-header {
            color: #f8f8f2 !important;
            font-size: 1rem;
            font-weight: 500;
            padding: 0.75rem !important;
        }

        .streamlit-expander-content {
            color: #f8f8f2 !important;
            padding: 0.75rem !important;
        }

        .stSidebar p {
            color: #f8f8f2;
            opacity: 0.7;
            font-size: 0.9rem;
            margin-bottom: 0.5rem;
        }

    </style>
    """, unsafe_allow_html=True)

def calcular_propriedades(largura, altura, espessura, raio, labio):
    area_labios = 2 * labio * espessura
    area_mesa = (largura - 2 * (raio + labio)) * espessura
    area_almas = 2 * (altura - 2 * raio) * espessura
    area_curvas = 4 * (math.pi * (raio + espessura/2) * espessura/2)

    area_total = area_labios + area_mesa + area_almas + area_curvas

    Ix = (espessura * (altura)**3)/12
    Iy = ((altura - 2 * raio) * espessura**3)/12 + 2 * ((espessura * (labio + raio)**3)/12 + espessura * (labio + raio) * (largura/2 - (labio + raio)/2)**2)

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
    """Cria uma visualização 2D mais fidedigna e clara do perfil U enrijecido"""
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_aspect('equal', adjustable='box')
    ax.set_facecolor('#282a36')

    perfil_color = '#f8f8f2'
    fill_color = '#6272a4'
    linha_espessura = 2  # Espessura da linha para melhor visualização

    # Desenhar a base (abaixo)
    ax.add_patch(Rectangle((raio, 0), largura - 2 * raio, espessura, facecolor=fill_color, edgecolor=perfil_color, linewidth=linha_espessura))

    # Desenhar as almas (laterais)
    ax.add_patch(Rectangle((0, espessura + raio), espessura, altura - 2 * espessura - 2 * raio, facecolor=fill_color, edgecolor=perfil_color, linewidth=linha_espessura))
    ax.add_patch(Rectangle((largura - espessura, espessura + raio), espessura, altura - 2 * espessura - 2 * raio, facecolor=fill_color, edgecolor=perfil_color, linewidth=linha_espessura))

    # Desenhar a mesa superior (acima)
    ax.add_patch(Rectangle((raio + espessura, altura - espessura), largura - 2 * (raio + espessura), espessura, facecolor=fill_color, edgecolor=perfil_color, linewidth=linha_espessura))

    # Desenhar os lábios (superiores)
    ax.add_patch(Rectangle((0, altura - espessura - labio), labio, espessura, facecolor=fill_color, edgecolor=perfil_color, linewidth=linha_espessura))
    ax.add_patch(Rectangle((largura - labio, altura - espessura - labio), labio, espessura, facecolor=fill_color, edgecolor=perfil_color, linewidth=linha_espessura))

    # Desenhar os cantos arredondados (arcos)
    raio_desenho = raio  # Usar o raio real para os arcos

    # Inferiores
    ax.add_patch(Arc((raio, espessura + raio), 2 * raio_desenho, 2 * raio_desenho, theta1=180, theta2=270, edgecolor=perfil_color, linewidth=linha_espessura))
    ax.add_patch(Arc((largura - raio, espessura + raio), 2 * raio_desenho, 2 * raio_desenho, theta1=270, theta2=360, edgecolor=perfil_color, linewidth=linha_espessura))

    # Superiores internos
    ax.add_patch(Arc((espessura + raio, altura - espessura - raio), 2 * raio_desenho, 2 * raio_desenho, theta1=90, theta2=180, edgecolor=perfil_color, linewidth=linha_espessura))
    ax.add_patch(Arc((largura - espessura - raio, altura - espessura - raio), 2 * raio_desenho, 2 * raio_desenho, theta1=0, theta2=90, edgecolor=perfil_color, linewidth=linha_espessura))

    # Ajustar limites para melhor visualização
    ax.set_xlim(-max(labio, espessura) - raio_desenho * 0.5, largura + max(labio, espessura) + raio_desenho * 0.5)
    ax.set_ylim(-raio_desenho * 0.5, altura + max(labio, espessura) + raio_desenho * 0.5)
    ax.axis('off')
    plt.tight_layout()
    return fig

def criar_metric_card(label, value):
    """Componente personalizado para métricas com cores vibrantes"""
    return f"""
    <div class="metric-container">
        <div class="metric-label" style="color:#f8f8f2; opacity: 0.8;">{label}</div>
        <div class="metric-value" style="color:#f1fa8c;">{value}</div>
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
        with st.expander("ℹ️ Dicas de Dimensionamento"):
            st.markdown("<p style='color:#f8f8f2; opacity: 0.7;'>- Lábios típicos: 10-20% da largura</p>", unsafe_allow_html=True)
            st.markdown("<p style='color:#f8f8f2; opacity: 0.7;'>- Raios comuns: 2-4x a espessura</p>", unsafe_allow_html=True)

    st.markdown("### 📐 Propriedades Geométricas")
    col_props1, col_props2 = st.columns(2)
    props = calcular_propriedades(largura, altura, espessura, raio, labio)

    with col_props1:
        st.markdown(criar_metric_card("Área da Seção Transversal", props['Área']), unsafe_allow_html=True)
        st.markdown(criar_metric_card("Mom. de Inércia (Ix)", props['Ix']), unsafe_allow_html=True)
        st.markdown(criar_metric_card("Mód. Resistente (Wx)", props['Wx']), unsafe_allow_html=True)
        st.markdown(criar_metric_card("Raio de Giração (rx)", props['rx']), unsafe_allow_html=True)

    with col_props2:
        st.markdown(criar_metric_card("Mom. de Inércia (Iy)", props['Iy']), unsafe_allow_html=True)
        st.markdown(criar_metric_card("Mód. Resistente (Wy)", props['Wy']), unsafe_allow_html=True)
        st.markdown(criar_metric_card("Raio de Giração (ry)", props['ry']), unsafe_allow_html=True)

    st.markdown("### 📏 Visualização do Perfil")
    st.markdown("<p style='color:#f8f8f2; opacity: 0.8;'>Representação da seção transversal</p>", unsafe_allow_html=True)
    fig = desenhar_perfil_2d(largura, altura, espessura, raio, labio)
    st.pyplot(fig)

    with st.expander("ℹ️ Detalhes da Visualização"):
        st.markdown("<p style='color:#f8f8f2; opacity: 0.7;'>- As dimensões são representadas fielmente.</p>", unsafe_allow_html=True)
        st.markdown("<p style='color:#f8f8f2; opacity: 0.7;'>- O contorno mostra a seção transversal exata.</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
