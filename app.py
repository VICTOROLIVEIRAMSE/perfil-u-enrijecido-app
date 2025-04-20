import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Arc

# (Função setup_theme permanece a mesma)

def calcular_propriedades(largura, altura, espessura, raio, labio):
    # (Função calcular_propriedades permanece a mesma)
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
    fill_color = '#6272a4'
    cota_color = '#f1fa8c'
    linha_espessura = 1

    # Desenhar o perfil Ue base (com dimensões genéricas para a forma)
    raio_base = 5
    espessura_base = 2
    labio_base = 10
    altura_base = 60
    largura_base = 100

    # Base
    ax.add_patch(Rectangle((raio_base, 0), largura_base - 2 * raio_base, espessura_base, facecolor=fill_color, edgecolor=perfil_color, linewidth=linha_espessura))
    # Almas
    ax.add_patch(Rectangle((0, espessura_base + raio_base), espessura_base, altura_base - 2 * espessura_base - 2 * raio_base, facecolor=fill_color, edgecolor=perfil_color, linewidth=linha_espessura))
    ax.add_patch(Rectangle((largura_base - espessura_base, espessura_base + raio_base), espessura_base, altura_base - 2 * espessura_base - 2 * raio_base, facecolor=fill_color, edgecolor=perfil_color, linewidth=linha_espessura))
    # Mesa superior
    ax.add_patch(Rectangle((raio_base + espessura_base, altura_base - espessura_base), largura_base - 2 * (raio_base + espessura_base), espessura_base, facecolor=fill_color, edgecolor=perfil_color, linewidth=linha_espessura))
    # Lábios
    ax.add_patch(Rectangle((0, altura_base - espessura_base - labio_base), labio_base, espessura_base, facecolor=fill_color, edgecolor=perfil_color, linewidth=linha_espessura))
    ax.add_patch(Rectangle((largura_base - labio_base, altura_base - espessura_base - labio_base), labio_base, espessura_base, facecolor=fill_color, edgecolor=perfil_color, linewidth=linha_espessura))
    # Cantos
    ax.add_patch(Arc((raio_base, espessura_base + raio_base), 2 * raio_base, 2 * raio_base, theta1=180, theta2=270, edgecolor=perfil_color, linewidth=linha_espessura))
    ax.add_patch(Arc((largura_base - raio_base, espessura_base + raio_base), 2 * raio_base, 2 * raio_base, theta1=270, theta2=360, edgecolor=perfil_color, linewidth=linha_espessura))
    ax.add_patch(Arc((espessura_base + raio_base, altura_base - espessura_base - raio_base), 2 * raio_base, 2 * raio_base, theta1=90, theta2=180, edgecolor=perfil_color, linewidth=linha_espessura))
    ax.add_patch(Arc((largura_base - espessura_base - raio_base, altura_base - espessura_base - raio_base), 2 * raio_base, 2 * raio_base, theta1=0, theta2=90, edgecolor=perfil_color, linewidth=linha_espessura))

    # Desenhar as cotas dinâmicas
    offset = 5  # Espaçamento das cotas

    # Cota da Largura (B)
    ax.annotate(f'{largura}', xy=(largura_base / 2, -offset - 5), xytext=(largura_base / 2, -offset - 15),
                arrowprops=dict(arrowstyle='-', color=cota_color, linewidth=0.5),
                ha='center', va='top', color=cota_color, fontsize=9)
    ax.plot([raio_base, raio_base], [-offset, 0], color=cota_color, linewidth=0.5)
    ax.plot([largura_base - raio_base, largura_base - raio_base], [-offset, 0], color=cota_color, linewidth=0.5)
    ax.plot([raio_base, largura_base - raio_base], [-offset, -offset], color=cota_color, linewidth=0.5)

    # Cota da Altura (H)
    ax.annotate(f'{altura}', xy=(-offset - 5, altura_base / 2), xytext=(-offset - 15, altura_base / 2),
                arrowprops=dict(arrowstyle='-', color=cota_color, linewidth=0.5),
                ha='right', va='center', rotation=90, color=cota_color, fontsize=9)
    ax.plot([-offset, 0], [espessura_base + raio_base, espessura_base + raio_base], color=cota_color, linewidth=0.5)
    ax.plot([-offset, 0], [altura_base - espessura_base - raio_base, altura_base - espessura_base - raio_base], color=cota_color, linewidth=0.5)
    ax.plot([-offset, -offset], [espessura_base + raio_base, altura_base - espessura_base - raio_base], color=cota_color, linewidth=0.5)

    # Cota da Espessura (t) - Exemplo em uma das abas
    ax.annotate(f'{espessura}', xy=(largura_base - espessura_base / 2, altura_base - espessura_base / 2), xytext=(largura_base + offset + 10, altura_base - espessura_base / 2),
                arrowprops=dict(arrowstyle='-', color=cota_color, linewidth=0.5),
                ha='left', va='center', color=cota_color, fontsize=9)
    ax.plot([largura_base - espessura_base, largura_base], [altura_base - espessura_base, altura_base - espessura_base], color=cota_color, linewidth=0.5)
    ax.plot([largura_base - espessura_base, largura_base - espessura_base], [altura_base - espessura_base, altura_base], color=cota_color, linewidth=0.5)
    ax.plot([largura_base, largura_base], [altura_base - espessura_base, altura_base], color=cota_color, linewidth=0.5)

    # Cota do Raio (r) - Exemplo em um dos cantos
    ax.annotate(f'{raio}', xy=(raio_base / 2, espessura_base + raio_base), xytext=(raio_base / 2 - 10, espessura_base + raio_base + 15),
                arrowprops=dict(arrowstyle='-', color=cota_color, linewidth=0.5, connectionstyle='arc3,rad=0.2'),
                ha='center', va='bottom', color=cota_color, fontsize=9)

    # Cota do Lábio (L) - Exemplo em um dos lábios
    ax.annotate(f'{labio}', xy=(labio_base / 2, altura_base - espessura_base - labio_base / 2), xytext=(labio_base / 2 - 10, altura_base - espessura_base - labio_base / 2 - 15),
                arrowprops=dict(arrowstyle='-', color=cota_color, linewidth=0.5),
                ha='center', va='top', color=cota_color, fontsize=9)
    ax.plot([0, 0], [altura_base - espessura_base - labio_base, altura_base - espessura_base], color=cota_color, linewidth=0.5)
    ax.plot([labio_base, labio_base], [altura_base - espessura_base - labio_base, altura_base - espessura_base], color=cota_color, linewidth=0.5)
    ax.plot([0, labio_base], [altura_base - espessura_base - labio_base, altura_base - espessura_base - labio_base], color=cota_color, linewidth=0.5)


    ax.set_xlim(-20, largura_base + 20)
    ax.set_ylim(-20, altura_base + 20)
    ax.axis('off')
    plt.tight_layout()
    return fig

def criar_metric_card(label, value):
    # (Função criar_metric_card permanece a mesma)
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

    st.markdown("### 📏 Visualização do Perfil com Cotas")
    st.markdown("<p style='color:#f8f8f2; opacity: 0.8;'>Representação da seção transversal com cotas</p>", unsafe_allow_html=True)
    fig = desenhar_perfil_ue_com_cotas(largura, altura, espessura, raio, labio)
    st.pyplot(fig)

    with st.expander("ℹ️ Detalhes da Visualização"):
        st.markdown("<p style='color:#f8f8f2; opacity: 0.7;'>- As cotas são atualizadas conforme os parâmetros.</p>", unsafe_allow_html=True)
        st.markdown("<p style='color:#f8f8f2; opacity: 0.7;'>- O perfil Ue é desenhado em uma escala fixa para clareza.</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
