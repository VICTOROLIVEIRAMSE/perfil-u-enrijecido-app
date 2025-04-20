import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# Configuração do tema aprimorado
def setup_theme():
    st.markdown("""
    <style>
        [data-testid="stAppViewContainer"] {
            background: white;
            color: #333333;
        }
        
        .st-emotion-cache-1y4p8pa {
            padding: 2rem 1rem 10rem;
        }
        
        [data-testid="stSidebar"] {
            background: #f0f2f6 !important;
            border-right: 1px solid #ddd;
        }
        
        .st-b7 {
            color: #333333 !important;
        }
        
        .st-c0 {
            background-color: white !important;
        }
        
        .stButton button {
            background: #4a6bdf !important;
            color: white !important;
            font-weight: bold;
            border: none;
            transition: all 0.3s;
        }
        
        .stButton button:hover {
            background: #3a56c0 !important;
            transform: scale(1.05);
        }
        
        .metric-container {
            background: white;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            border-left: 5px solid #4a6bdf;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: all 0.3s;
            color: #333333;
        }
        
        .metric-container:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }
        
        .metric-value {
            font-size: 1.5rem;
            font-weight: bold;
            color: #4a6bdf;
        }
        
        .metric-label {
            font-size: 1rem;
            color: #555555;
        }
        
        .title {
            color: #4a6bdf !important;
            font-size: 2.5rem !important;
            margin-bottom: 0.5rem !important;
        }
        
        .subheader {
            color: #555555 !important;
            font-size: 1.2rem !important;
            margin-bottom: 2rem !important;
        }
        
        /* Garantir que todo texto esteja visível */
        * {
            color: #333333 !important;
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

def desenhar_perfil_3d(largura, altura, espessura, raio, labio, comprimento=300):
    """Cria uma visualização 3D profissional do perfil"""
    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(111, projection='3d')
    
    # Cores
    cor_perfil = '#4a6bdf'
    cor_preenchimento = '#a0b4f8'
    
    # Definindo os vértices do perfil U
    vertices = []
    
    # Face frontal
    vertices.append([(0, 0, 0), (largura, 0, 0), (largura, altura, 0), (0, altura, 0)])
    
    # Face traseira
    vertices.append([(0, 0, comprimento), (largura, 0, comprimento), (largura, altura, comprimento), (0, altura, comprimento)])
    
    # Lados
    vertices.append([(0, 0, 0), (0, 0, comprimento), (0, altura, comprimento), (0, altura, 0)])
    vertices.append([(largura, 0, 0), (largura, 0, comprimento), (largura, altura, comprimento), (largura, altura, 0)])
    
    # Mesa superior
    vertices.append([(0, altura, 0), (largura, altura, 0), (largura, altura, comprimento), (0, altura, comprimento)])
    
    # Adicionando os lábios enrijecedores
    vertices.append([(0, altura-espessura-labio, 0), (labio, altura-espessura-labio, 0), 
                    (labio, altura-espessura, 0), (0, altura-espessura, 0)])
    vertices.append([(0, altura-espessura-labio, comprimento), (labio, altura-espessura-labio, comprimento), 
                    (labio, altura-espessura, comprimento), (0, altura-espessura, comprimento)])
    vertices.append([(largura, altura-espessura-labio, 0), (largura-labio, altura-espessura-labio, 0), 
                    (largura-labio, altura-espessura, 0), (largura, altura-espessura, 0)])
    vertices.append([(largura, altura-espessura-labio, comprimento), (largura-labio, altura-espessura-labio, comprimento), 
                    (largura-labio, altura-espessura, comprimento), (largura, altura-espessura, comprimento)])
    
    # Criando as faces 3D
    faces = Poly3DCollection(vertices, alpha=0.8, linewidths=1, edgecolors='#333333', facecolors=cor_preenchimento)
    ax.add_collection3d(faces)
    
    # Configurações do gráfico
    ax.set_xlim(0, largura + 50)
    ax.set_ylim(0, altura + 50)
    ax.set_zlim(0, comprimento)
    ax.set_box_aspect([1, 1, 2])
    
    # Ângulo de visualização
    ax.view_init(elev=25, azim=45)
    
    # Rótulos dos eixos
    ax.set_xlabel('Largura (mm)')
    ax.set_ylabel('Altura (mm)')
    ax.set_zlabel('Comprimento (mm)')
    
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
        st.markdown("### 🎨 Visualização 3D do Perfil")
        fig = desenhar_perfil_3d(largura, altura, espessura, raio, labio)
        st.pyplot(fig)
        
        st.markdown("---")
        st.markdown("**Visualização 3D interativa:**")
        st.markdown("- Use o mouse para rotacionar o perfil")
        st.markdown("- Scroll para zoom in/out")

if __name__ == "__main__":
    main()
