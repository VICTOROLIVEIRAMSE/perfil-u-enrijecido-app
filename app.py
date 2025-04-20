import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon

# Configuração do tema aprimorado
def setup_theme():
    st.markdown("""
    <style>
        [data-testid="stAppViewContainer"] {
            background: #282a36;
            color: #f8f8f2;
        }
        
        .st-emotion-cache-1y4p8pa {
            padding: 2rem 1rem 10rem;
        }
        
        [data-testid="stSidebar"] {
            background: #44475a !important;
            border-right: 1px solid #6272a4;
        }
        
        .st-b7 {
            color: #f8f8f2 !important;
        }
        
        .st-c0 {
            background-color: #44475a !important;
        }
        
        .stButton button {
            background: #bd93f9 !important;
            color: #282a36 !important;
            font-weight: bold;
            border: none;
            transition: all 0.3s;
        }
        
        .stButton button:hover {
            background: #ff79c6 !important;
            transform: scale(1.05);
        }
        
        .metric-container {
            background: #44475a;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            border-left: 5px solid #bd93f9;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: all 0.3s;
        }
        
        .metric-container:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }
        
        .metric-value {
            font-size: 1.5rem;
            font-weight: bold;
            color: #50fa7b;
        }
        
        .metric-label {
            font-size: 1rem;
            color: #f8f8f2;
            opacity: 0.8;
        }
        
        .title {
            color: #ff79c6 !important;
            font-size: 2.5rem !important;
            margin-bottom: 0.5rem !important;
        }
        
        .subheader {
            color: #bd93f9 !important;
            font-size: 1.2rem !important;
            margin-bottom: 2rem !important;
        }
    </style>
    """, unsafe_allow_html=True)

def calcular_propriedades(largura, altura, espessura, raio, labio):
    """Calcula as propriedades geométricas com precisão"""
    # Áreas dos componentes
    area_labios = 2 * labio * espessura
    area_mesa = (largura - 2 * (raio + labio)) * espessura
    area_almas = 2 * (altura - 2 * raio) * espessura
    area_curvas = 4 * (math.pi * (raio + espessura/2) * espessura)
    
    area_total = area_labios + area_mesa + area_almas + area_curvas
    
    # Centroide
    xg = largura / 2  # Simétrico
    yg = altura / 2
    
    # Momentos de inércia (cálculo mais preciso)
    Ix = (espessura * (altura - 2*raio)**3)/12 + 2*( (labio*espessura**3)/12 + labio*espessura*(altura/2 - espessura/2)**2 )
    Ix += ( (largura - 2*(raio + labio)) * espessura**3 )/12 + (largura - 2*(raio + labio)) * espessura * (altura/2)**2
    
    Iy = ( (altura - 2*raio) * espessura**3 )/12 + 2*( (espessura * labio**3)/12 + labio*espessura*(largura/2 - labio/2)**2 )
    Iy += ( espessura * (largura - 2*(raio + labio))**3 )/12
    
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

def desenhar_perfil(largura, altura, espessura, raio, labio):
    """Cria uma visualização profissional do perfil"""
    fig, ax = plt.subplots(figsize=(10, 6), facecolor='#282a36')
    ax.set_facecolor('#282a36')
    
    # Definindo as cores do tema Dracula
    cor_perfil = '#bd93f9'
    cor_preenchimento = '#44475a'
    cor_fundo = '#282a36'
    cor_texto = '#f8f8f2'
    
    # Desenho do perfil U enrijecido
    # Mesa superior
    mesa = Rectangle((0, altura-espessura), largura, espessura, 
                    linewidth=2, edgecolor=cor_perfil, facecolor=cor_preenchimento)
    
    # Almas
    alma_esq = Rectangle((0, 0), espessura, altura-espessura,
                        linewidth=2, edgecolor=cor_perfil, facecolor=cor_preenchimento)
    
    alma_dir = Rectangle((largura-espessura, 0), espessura, altura-espessura,
                        linewidth=2, edgecolor=cor_perfil, facecolor=cor_preenchimento)
    
    # Lábios enrijecedores
    labio_esq = Rectangle((espessura, altura-espessura-labio), labio, espessura,
                         linewidth=2, edgecolor=cor_perfil, facecolor=cor_preenchimento)
    
    labio_dir = Rectangle((largura-espessura-labio, altura-espessura-labio), labio, espessura,
                         linewidth=2, edgecolor=cor_perfil, facecolor=cor_preenchimento)
    
    # Adicionando elementos ao plot
    for patch in [mesa, alma_esq, alma_dir, labio_esq, labio_dir]:
        ax.add_patch(patch)
    
    # Configurações do gráfico
    ax.set_xlim(-10, largura + 10)
    ax.set_ylim(-10, altura + 10)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Adicionando dimensões
    ax.annotate(f"{largura} mm", xy=(largura/2, altura+5), 
               ha='center', va='center', color=cor_texto, fontsize=10)
    ax.annotate(f"{altura} mm", xy=(-5, altura/2), 
               ha='right', va='center', color=cor_texto, fontsize=10, rotation=90)
    ax.annotate(f"Labio: {labio} mm", xy=(largura/2, altura-espessura-labio/2), 
               ha='center', va='center', color=cor_texto, fontsize=9)
    
    plt.tight_layout()
    return fig

def criar_metric_card(label, value):
    """Componente personalizado para métricas"""
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
        st.markdown("**Dicas:**")
        st.markdown("- Lábios típicos: 10-20% da largura")
        st.markdown("- Raios comuns: 2-4x a espessura")
    
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
        st.markdown("### 🎨 Visualização do Perfil")
        fig = desenhar_perfil(largura, altura, espessura, raio, labio)
        st.pyplot(fig)
        
        st.markdown("---")
        st.markdown("**Legenda:**")
        st.markdown("- <span style='color:#bd93f9'>**Linhas roxas**</span>: Contorno do perfil", unsafe_allow_html=True)
        st.markdown("- <span style='color:#44475a'>**Área cinza**</span>: Seção transversal", unsafe_allow_html=True)
        st.markdown("- Dimensões em milímetros (mm)")

if __name__ == "__main__":
    main()
