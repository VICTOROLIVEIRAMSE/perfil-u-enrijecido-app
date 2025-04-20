import streamlit as st
import math
from streamlit.components.v1 import html

# Configuração do tema Dracula
def inject_dracula_theme():
    dracula_theme = """
    <style>
        :root {
            --primary: #ff79c6;
            --background: #282a36;
            --secondary: #bd93f9;
            --text: #f8f8f2;
            --accent: #50fa7b;
            --highlight: #6272a4;
        }
        
        .stApp {
            background-color: var(--background);
            color: var(--text);
        }
        
        .stTextInput>div>div>input, .stNumberInput>div>div>input {
            color: var(--text);
            background-color: #44475a;
            border-color: var(--highlight);
        }
        
        .stSelectbox>div>div>select {
            color: var(--text);
            background-color: #44475a;
        }
        
        .stButton>button {
            background-color: var(--secondary);
            color: var(--background);
            border: none;
            font-weight: bold;
        }
        
        .stButton>button:hover {
            background-color: var(--primary);
            color: var(--background);
        }
        
        .metric {
            background-color: #44475a;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 10px;
            border-left: 4px solid var(--secondary);
        }
        
        h1, h2, h3, h4, h5, h6 {
            color: var(--primary);
        }
        
        .stMarkdown {
            color: var(--text);
        }
    </style>
    """
    st.markdown(dracula_theme, unsafe_allow_html=True)

def calcular_propriedades_geometricas(largura, altura, espessura, raio, comprimento_labio):
    """Calcula as propriedades geométricas de um perfil U enrijecido conforme NBR 14762"""
    
    # Cálculos geométricos
    area_labio = comprimento_labio * espessura
    area_mesa = (largura - 2 * raio - 2 * comprimento_labio) * espessura
    area_alma = (altura - 2 * raio) * espessura
    area_curvas = math.pi * (raio + espessura/2) * espessura
    
    area_total = 2 * area_labio + area_mesa + 2 * area_alma + 4 * area_curvas
    
    # Centroide
    momento_labio_esq = area_labio * (comprimento_labio/2)
    momento_curva_esq = area_curvas * (comprimento_labio + raio/2)
    momento_alma_esq = area_alma * (comprimento_labio + raio + espessura/2)
    momento_mesa = area_mesa * (largura/2)
    momento_curva_dir = area_curvas * (largura - comprimento_labio - raio/2)
    momento_labio_dir = area_labio * (largura - comprimento_labio/2)
    
    xg = (momento_labio_esq + momento_curva_esq + momento_alma_esq + 
          momento_mesa + momento_curva_dir + momento_labio_dir) / area_total
    yg = altura / 2
    
    # Momento de inércia
    i_labio_x = (comprimento_labio * espessura**3)/12 + area_labio * (altura - espessura/2)**2
    i_mesa_x = (espessura * (largura - 2*raio - 2*comprimento_labio)**3)/12 + area_mesa * (altura/2)**2
    i_alma_x = (espessura * (altura - 2*raio)**3)/12
    i_curva_x = 0.149 * raio * espessura**3 + area_curvas * (altura/2 - raio/2)**2
    ix = 2 * i_labio_x + i_mesa_x + 2 * i_alma_x + 4 * i_curva_x
    
    i_labio_y = (espessura * comprimento_labio**3)/12 + area_labio * (comprimento_labio/2 - xg)**2
    i_mesa_y = (espessura**3 * (largura - 2*raio - 2*comprimento_labio))/12 + area_mesa * (largura/2 - xg)**2
    i_alma_y = ((altura - 2*raio) * espessura**3)/12 + area_alma * (comprimento_labio + raio + espessura/2 - xg)**2
    i_curva_y = 0.149 * raio**3 * espessura + area_curvas * (comprimento_labio + raio/2 - xg)**2
    iy = 2 * i_labio_y + i_mesa_y + 2 * i_alma_y + 4 * i_curva_y
    
    # Outras propriedades
    wx = ix / (altura/2)
    wy = iy / max(xg, largura - xg)
    rx = math.sqrt(ix / area_total)
    ry = math.sqrt(iy / area_total)
    perimetro = 2 * (largura + altura) - 8 * raio + 2 * math.pi * raio
    j = (perimetro * espessura**3) / 3
    h = altura - espessura
    b = largura - espessura
    cw = (h**2 * b**3 * espessura) / 12 * ((6 * comprimento_labio + b) / (12 * comprimento_labio + b))
    
    return {
        'Área (Ag)': area_total,
        'Centroide X (Xg)': xg,
        'Centroide Y (Yg)': yg,
        'Mom. Inércia X (Ix)': ix,
        'Mom. Inércia Y (Iy)': iy,
        'Mód. Resistente X (Wx)': wx,
        'Mód. Resistente Y (Wy)': wy,
        'Raio de Giração X (rx)': rx,
        'Raio de Giração Y (ry)': ry,
        'Const. Torção (J)': j,
        'Const. Empenamento (Cw)': cw
    }

def main():
    inject_dracula_theme()
    
    st.title('📐 Dimensionamento de Perfil U Enrijecido')
    st.markdown("### Cálculo conforme NBR 14724 - Dimensionamento de estruturas de aço constituídas por perfis formados a frio")
    
    with st.expander("ℹ️ Instruções", expanded=False):
        st.markdown("""
        - Preencha as dimensões do perfil em milímetros (mm)
        - Clique em **Calcular Propriedades**
        - Os resultados serão exibidos abaixo
        """)
    
    with st.form("dados_perfil"):
        st.markdown("### 📏 Dimensões do Perfil")
        col1, col2 = st.columns(2)
        
        with col1:
            largura = st.number_input("Largura da mesa (mm)", min_value=10.0, value=100.0, step=1.0)
            altura = st.number_input("Altura da alma (mm)", min_value=10.0, value=50.0, step=1.0)
            
        with col2:
            espessura = st.number_input("Espessura (mm)", min_value=0.5, value=1.5, step=0.1)
            raio = st.number_input("Raio de dobramento (mm)", min_value=0.5, value=3.0, step=0.5)
            comprimento_labio = st.number_input("Comprimento do lábio enrijecedor (mm)", min_value=0.0, value=10.0, step=1.0)
        
        submitted = st.form_submit_button("🚀 Calcular Propriedades", use_container_width=True)

    if submitted:
        st.markdown("---")
        st.markdown("## 📊 Resultados das Propriedades Geométricas")
        
        propriedades = calcular_propriedades_geometricas(largura, altura, espessura, raio, comprimento_labio)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Área (Ag)", f"{propriedades['Área (Ag)']:.2f} mm²", help="Área total da seção transversal")
            st.metric("Centroide X (Xg)", f"{propriedades['Centroide X (Xg)']:.2f} mm", help="Posição do centroide no eixo X")
            st.metric("Centroide Y (Yg)", f"{propriedades['Centroide Y (Yg)']:.2f} mm", help="Posição do centroide no eixo Y")
            st.metric("Mom. Inércia X (Ix)", f"{propriedades['Mom. Inércia X (Ix)']:.2f} mm⁴", help="Momento de inércia em relação ao eixo X")
            
        with col2:
            st.metric("Mom. Inércia Y (Iy)", f"{propriedades['Mom. Inércia Y (Iy)']:.2f} mm⁴", help="Momento de inércia em relação ao eixo Y")
            st.metric("Mód. Resistente X (Wx)", f"{propriedades['Mód. Resistente X (Wx)']:.2f} mm³", help="Módulo resistente elástico em X")
            st.metric("Mód. Resistente Y (Wy)", f"{propriedades['Mód. Resistente Y (Wy)']:.2f} mm³", help="Módulo resistente elástico em Y")
            st.metric("Raio de Giração X (rx)", f"{propriedades['Raio de Giração X (rx)']:.2f} mm", help="Raio de giração em relação ao eixo X")
        
        st.metric("Raio de Giração Y (ry)", f"{propriedades['Raio de Giração Y (ry)']:.2f} mm", help="Raio de giração em relação ao eixo Y")
        st.metric("Constante de Torção (J)", f"{propriedades['Const. Torção (J)']:.2f} mm⁴", help="Constante de torção de Saint-Venant")
        st.metric("Constante de Empenamento (Cw)", f"{propriedades['Const. Empenamento (Cw)']:.2e} mm⁶", help="Constante de empenamento da seção")
        
        # Visualização esquemática do perfil
        st.markdown("---")
        st.markdown("## 🖍️ Visualização Esquemática")
        
        # Código SVG para representar o perfil U
        svg_code = f"""
        <svg width="400" height="300" viewBox="0 0 {largura + 50} {altura + 50}" xmlns="http://www.w3.org/2000/svg">
            <!-- Perfil U -->
            <path d="
                M 20,20
                h {comprimento_labio}
                a {raio},{raio} 0 0 1 {raio},{raio}
                v {altura - 2*raio}
                a {raio},{raio} 0 0 1 -{raio},{raio}
                h -{comprimento_labio}
                h -{largura - 2*comprimento_labio - 2*raio}
                h -{comprimento_labio}
                a {raio},{raio} 0 0 1 -{raio},-{raio}
                v -{altura - 2*raio}
                a {raio},{raio} 0 0 1 {raio},-{raio}
                h {comprimento_labio}
                z
            " fill="none" stroke="#bd93f9" stroke-width="{espessura}" />
            
            <!-- Dimensões -->
            <line x1="20" y1="{altura + 30}" x2="{20 + largura}" y2="{altura + 30}" stroke="#ff79c6" stroke-width="1.5" stroke-dasharray="5,5" />
            <text x="{20 + largura/2}" y="{altura + 40}" fill="#f8f8f2" font-size="12" text-anchor="middle">{largura} mm</text>
            
            <line x1="10" y1="20" x2="10" y2="{20 + altura}" stroke="#ff79c6" stroke-width="1.5" stroke-dasharray="5,5" />
            <text x="5" y="{20 + altura/2}" fill="#f8f8f2" font-size="12" text-anchor="middle" transform="rotate(-90,5,{20 + altura/2})">{altura} mm</text>
            
            <!-- Legenda -->
            <text x="20" y="15" fill="#50fa7b" font-size="10">Lábio: {comprimento_labio} mm</text>
            <text x="{20 + largura/2}" y="{20 + altura + 20}" fill="#50fa7b" font-size="10">R: {raio} mm</text>
        </svg>
        """
        
        st.components.v1.html(svg_code, height=300)

if __name__ == "__main__":
    main()
