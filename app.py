import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Arc

# Configuração do tema Dracula
def setup_theme():
    dracula_theme = """
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
            color: #f8f8f2 !important;
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
            color: #f1fa8c;
            margin-bottom: 0.2rem;
        }
        .metric-label {
            font-size: 0.95rem;
            color: #f8f8f2;
            opacity: 0.8;
        }
        .title {
            color: #ff79c6 !important;
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
        .stSidebar h2, .stSidebar label, .stSidebar p, .stSidebar div {
            color: #f8f8f2 !important;
        }
        .stSidebar p {
            opacity: 0.7;
            font-size: 0.9rem;
            margin-bottom: 0.5rem;
        }
    </style>
    """
    st.markdown(dracula_theme, unsafe_allow_html=True)

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

def desenhar_perfil_ue_com_cotas(largura, altura, espessura, raio, labio):
    """Desenha o perfil Ue fixo e sobrepõe as cotas dinâmicas."""
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_aspect('equal', adjustable='box')
    ax.set_facecolor('#282a36')
    perfil_color = '#f8f8f2'
    cota_color = '#f1fa8c'
    linha_espessura = 1

    # Desenhar o perfil Ue base (com dimensões genéricas para a forma)
    raio_base = 5
    espessura_base = 2
    labio_base = 10
    altura_base = 60
    largura_base = 100

    # Base
    ax.add_patch(Rectangle((raio_base, 0), largura_base - 2 * raio_base, espessura_base, facecolor='#6272a4', edgecolor=perfil_color, linewidth=linha_espessura))
    # Almas
    ax.add_patch(Rectangle((0, espessura_base + raio_base), espessura_base, altura_base - 2 * espessura_base - 2 * raio_base, facecolor='#6272a4', edgecolor=perfil_color, linewidth=linha_espessura))
    ax.add_patch(Rectangle((largura_base - espessura_base, espessura_base + raio_base), espessura_base, altura_base - 2 * espessura_base - 2 * raio_base, facecolor='#6272a4', edgecolor=perfil_color, linewidth=linha_espessura))
    # Mesa superior
    ax.add_patch(Rectangle((raio_base + espessura_base, altura_base - espessura_base), largura_base - 2 * (raio_base + espessura_base), espessura_base, facecolor='#6272a4', edgecolor=perfil_color,
