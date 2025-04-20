import streamlit as st
import numpy as np
import math
from scipy.optimize import newton

# Constants
E_aço = 205000  # MPa (Modulus of elasticity)
G_aço = 78846.15  # MPa (Shear modulus)
gamma_a1 = 1.1  # Safety factor
kv_shear = 5.34  # Shear buckling coefficient for unstiffened webs

# --- Geometric Property Calculations ---
def calculate_gross_properties(bf, bw, t, rm, cm):
    # bf: flange width (mm)
    # bw: web height (mm)
    # t: thickness (mm)
    # rm: internal radius (mm)
    # cm: lip length (mm)

    # Check for valid inputs
    if any(dim is None or dim <= 0 for dim in [bf, bw, t]):
        st.error("Dimensions (width, height, thickness) must be greater than zero.")
        return None

    # Area (A) - NBR 14762
    A_bruta = t * (bw + 2*bf + 2*cm)  # mm²

    # Calculate CG x-coordinate (distance from back of web face to CG)
    # Using standard formulas for U-section with lips
    if A_bruta == 0:
        xg_calc_std = 0.0
    else:
        # Web contribution
        web_area = bw * t
        web_cg = t/2
        
        # Flange contribution
        flange_area = bf * t
        flange_cg = t + rm + (bf - t - rm)/2
        
        # Lip contribution
        lip_area = cm * t
        lip_cg = t + rm + (bf - t - rm) + (cm - t - rm)/2
        
        sum_moments = (web_area * web_cg + 
                      2 * (flange_area * flange_cg) + 
                      2 * (lip_area * lip_cg))
        xg_calc_std = sum_moments / A_bruta  # mm from back of web

    # Ix (about axis through CG, parallel to flanges) - NBR 14762
    Ix_bruta = (t * bw**3)/12 + 2*( (bf * t**3)/12 + bf * t * (bw/2 + t/2)**2 ) + \
               2*( (cm * t**3)/12 + cm * t * (bw/2 + t/2 + rm + (cm - t)/2)**2 )

    # Iy (about axis of symmetry, through CG) - NBR 14762
    Iy_bruta = (bw * t**3)/12 + bw * t * (xg_calc_std - t/2)**2 + \
               2*( (t * bf**3)/12 + bf * t * (xg_calc_std - flange_cg)**2 ) + \
               2*( (t * cm**3)/12 + cm * t * (xg_calc_std - lip_cg)**2 )

    # It (Torsional constant J) - NBR 14762
    It_bruta = (t**3 / 3) * (2*bf + bw + 2*cm)  # mm4

    # Warping constant (Cw) - NBR 14762 Annex G for U-sections
    h = bw - 2*t  # Clear web height
    Cw = (t * bf**3 * h**2)/12 * (3*bf + 2*h)/(6*bf + h)  # mm6

    # Shear center (x0) - NBR 14762 Annex G
    x0 = - (3*bf**2)/(6*bf + h)  # mm from centroid

    # Polar radius of gyration (r0) - NBR 14762 eq. 7.7
    rx = np.sqrt(Ix_bruta/A_bruta)
    ry = np.sqrt(Iy_bruta/A_bruta)
    y0 = 0  # Symmetry about x-axis
    r0 = np.sqrt(rx**2 + ry**2 + x0**2 + y0**2)

    # Section moduli
    Wx_bruto = 2 * Ix_bruta / bw  # mm3
    Wy_bruto = Iy_bruta / max(xg_calc_std, (t + 2*rm + 2*bf + 2*cm - xg_calc_std))  # mm3

    # Radii of gyration
    rx_bruto = np.sqrt(Ix_bruta / A_bruta)
    ry_bruto = np.sqrt(Iy_bruta / A_bruta)

    return {
        "A_bruta": A_bruta, "Ix_bruta": Ix_bruta, "Iy_bruta": Iy_bruta,
        "Wx_bruto": Wx_bruto, "Wy_bruto": Wy_bruto,
        "rx_bruto": rx_bruto, "ry_bruto": ry_bruto,
        "It_bruta": It_bruta, "Cw": Cw,
        "xg": xg_calc_std, "x0": x0, "y0": y0,
        "r0": r0,
        "t": t, "bw": bw, "bf": bf, "rm": rm, "cm": cm
    }

# --- Effective Width Calculations (NBR 14762 Section 3.3) ---
def calculate_effective_width(element_type, b, t, sigma, fy, E=E_aço):
    """
    Calculate effective width according to NBR 14762 Section 3.3
    element_type: 'AA' (unstiffened), 'AL' (edge stiffened), or 'AEF' (intermediate stiffened)
    b: element width (mm)
    t: thickness (mm)
    sigma: applied stress (MPa)
    fy: yield strength (MPa)
    """
    k = {
        'AA': 4.0,    # Unstiffened element under uniform compression
        'AL': 0.43,   # Edge stiffened element
        'AEF': 4.0    # Intermediate stiffened element (simplified)
    }.get(element_type, 4.0)
    
    lambda_p = (b/t) / (0.95 * np.sqrt(k * E / abs(sigma)))
    
    if lambda_p <= 0.673:
        return b  # Fully effective
    
    rho = (1 - 0.22/lambda_p) / lambda_p
    return rho * b

def calculate_effective_properties(gross_props, N_sd, Mx_sd, My_sd, fy):
    """
    Calculate effective section properties according to NBR 14762 Section 3.3
    """
    # Initial stress estimation (simplified approach)
    sigma_max = abs(N_sd/gross_props["A_bruta"]) + \
                abs(Mx_sd/gross_props["Wx_bruto"]) + \
                abs(My_sd/gross_props["Wy_bruto"])
    
    # Adjust to not exceed fy
    sigma = min(sigma_max, fy)
    
    # Calculate effective widths for each element
    t = gross_props["t"]
    
    # Web (AA element)
    b_web = gross_props["bw"] - 2*gross_props["rm"]
    be_web = calculate_effective_width('AA', b_web, t, sigma, fy)
    
    # Flanges (AL element)
    b_flange = gross_props["bf"] - gross_props["rm"] - t/2
    be_flange = calculate_effective_width('AL', b_flange, t, sigma, fy)
    
    # Lips (AL element)
    be_lip = calculate_effective_width('AL', gross_props["cm"] - t/2 - gross_props["rm"], t, sigma, fy)
    
    # Calculate effective area (simplified - full implementation would need iterative approach)
    A_efetiva = t * (be_web + 2*be_flange + 2*be_lip)
    
    # Simplified effective section modulus (conservative)
    Wx_efetivo = gross_props["Wx_bruto"] * (A_efetiva / gross_props["A_bruta"])
    Wy_efetivo = gross_props["Wy_bruto"] * (A_efetiva / gross_props["A_bruta"])
    
    # CG shift (simplified)
    CG_shift_ef = 0.1 * gross_props["xg"] * (1 - A_efetiva/gross_props["A_bruta"])
    
    return {
        "A_efetiva": A_efetiva,
        "Wx_efetivo": Wx_efetivo,
        "Wy_efetivo": Wy_efetivo,
        "CG_shift_ef": CG_shift_ef,
        "be_web": be_web,
        "be_flange": be_flange,
        "be_lip": be_lip
    }

# --- Elastic Buckling Loads (NBR 14762 Section 7.7.2) ---
def calculate_elastic_buckling_loads(gross_props, le_x, le_y, le_t):
    """
    Calculate elastic buckling loads (Ne) according to NBR 14762 Section 7.7.2
    """
    # Flexural buckling about x-axis
    Nex = (np.pi**2 * E_aço * gross_props["Ix_bruta"]) / (le_x**2) if le_x > 0 else float('inf')
    
    # Flexural buckling about y-axis
    Ney = (np.pi**2 * E_aço * gross_props["Iy_bruta"]) / (le_y**2) if le_y > 0 else float('inf')
    
    # Torsional buckling
    if gross_props["r0"] > 0 and le_t > 0:
        term1 = (np.pi**2 * E_aço * gross_props["Cw"]) / (le_t**2)
        term2 = G_aço * gross_props["It_bruta"]
        Net = (1 / gross_props["r0"]**2) * (term1 + term2)
    else:
        Net = float('inf')
    
    # Flexural-torsional buckling (for mono-symmetric sections)
    x0 = gross_props["x0"]
    r0 = gross_props["r0"]
    
    if r0 > 0:
        denominator = 2 * (1 - (x0/r0)**2)
        if denominator != 0:
            term = (4 * Nex * Net * (1 - (x0/r0)**2)) / (Nex + Net)**2
            if term <= 1:
                Next = ((Nex + Net) / denominator) * (1 - np.sqrt(1 - term))
            else:
                Next = float('inf')
        else:
            Next = float('inf')
    else:
        Next = float('inf')
    
    # Minimum buckling load
    Ne = min(Nex, Ney, Net, Next)
    
    return {"Nex": Nex, "Ney": Ney, "Net": Net, "Next": Next, "Ne": Ne}

# --- Global Buckling Reduction Factor (NBR 14762 Section 7.7.3) ---
def calculate_global_buckling_reduction_factor(Ne, A_ef, fy, buckling_type='flexural'):
    """
    Calculate reduction factor (rho) according to NBR 14762 Section 7.7.3
    buckling_type: 'flexural' (curve a/b/c), 'torsional' (curve b), or 'flexural-torsional' (curve b)
    """
    # Determine imperfection factor (alpha)
    if buckling_type in ['torsional', 'flexural-torsional']:
        alpha = 0.34  # Curve b
    else:
        # For flexural buckling, would need to determine curve based on section type
        alpha = 0.34  # Default to curve b
    
    # Slenderness ratio
    lambda0 = np.sqrt(A_ef * fy / Ne) if Ne > 0 else 0
    
    # Reduction factor calculation
    beta = 0.5 * (1 + alpha * (lambda0 - 0.2) + lambda0**2)
    rho = 1 / (beta + np.sqrt(beta**2 - lambda0**2)) if (beta**2 - lambda0**2) > 0 else 1.0
    rho = min(rho, 1.0)
    
    return {"lambda0": lambda0, "rho": rho}

# --- Distortional Buckling (NBR 14762 Section 7.7.4) ---
def calculate_distortional_buckling(gross_props, fy, L_dist):
    """
    Simplified calculation of distortional buckling resistance for U-sections
    Based on NBR 14762 Annex D and simplified methods
    """
    # Simplified method parameters
    b = gross_props["bf"]
    d = gross_props["cm"]
    h = gross_props["bw"] - 2*gross_props["t"]
    t = gross_props["t"]
    
    # Elastic critical stress for distortional buckling (simplified)
    sigma_dist = (0.5 * E_aço * (t/d)**2) / (1 - gross_props["rm"]/d)**3
    
    # Slenderness for distortional buckling
    lambda_dist = np.sqrt(fy / sigma_dist) if sigma_dist > 0 else float('inf')
    
    # Distortional buckling resistance
    if lambda_dist < 1.414:
        Nd_Rd = gross_props["A_bruta"] * fy * (1 - 0.25 * lambda_dist**2) / gamma_a1
    elif lambda_dist <= 3.6:
        Nd_Rd = gross_props["A_bruta"] * fy * (0.055 * (lambda_dist - 3.6)**2 + 0.237) / gamma_a1
    else:
        Nd_Rd = 0
    
    return {"sigma_dist": sigma_dist, "lambda_dist": lambda_dist, "Nd_Rd": Nd_Rd}

# --- Compression Resistance (NBR 14762 Section 7.7) ---
def calculate_compression_resistance(gross_props, effective_props, elastic_loads, fy, L_dist):
    """
    Calculate compression resistance according to NBR 14762 Section 7.7
    """
    # Yield resistance
    Ny_Rd = effective_props["A_efetiva"] * fy / gamma_a1
    
    # Global buckling resistance
    global_buckling = calculate_global_buckling_reduction_factor(
        elastic_loads["Ne"], 
        effective_props["A_efetiva"], 
        fy,
        buckling_type='flexural-torsional'  # Typical for U-sections
    )
    Nf_Rd = global_buckling["rho"] * effective_props["A_efetiva"] * fy / gamma_a1
    
    # Distortional buckling resistance
    distortional = calculate_distortional_buckling(gross_props, fy, L_dist)
    Nd_Rd = distortional["Nd_Rd"]
    
    # Tensile resistance
    Nt_Rd = gross_props["A_bruta"] * fy / gamma_a1
    
    # Final compression resistance is minimum of all checks
    Nc_Rd = min(Ny_Rd, Nf_Rd, Nd_Rd) if Nd_Rd > 0 else min(Ny_Rd, Nf_Rd)
    
    return {
        "Ny_Rd": Ny_Rd,
        "Nf_Rd": Nf_Rd,
        "Nd_Rd": Nd_Rd,
        "Nc_Rd": Nc_Rd,
        "Nt_Rd": Nt_Rd,
        "lambda0": global_buckling["lambda0"],
        "rho": global_buckling["rho"],
        "lambda_dist": distortional["lambda_dist"],
        "sigma_dist": distortional["sigma_dist"]
    }

# --- Bending Resistance (NBR 14762 Section 8) ---
def calculate_bending_resistance(gross_props, effective_props, fy, Lb, Cb=1.0):
    """
    Calculate bending resistance according to NBR 14762 Section 8
    """
    # Yield resistance
    Mx_Rd_yield = effective_props["Wx_efetivo"] * fy / gamma_a1
    My_Rd_yield = effective_props["Wy_efetivo"] * fy / gamma_a1
    
    # Lateral-torsional buckling resistance
    # Elastic critical moment (simplified for U-sections)
    Me = Cb * np.pi / Lb * np.sqrt(
        E_aço * gross_props["Iy_bruta"] * 
        (G_aço * gross_props["It_bruta"] + (np.pi**2 * E_aço * gross_props["Cw"]) / Lb**2)
    )
    
    # Non-dimensional slenderness
    lambda0 = np.sqrt(gross_props["Wx_bruto"] * fy / Me) if Me > 0 else 0
    
    # Reduction factor for LTB
    if lambda0 <= 0.6:
        rho_LTB = 1.0
    elif 0.6 < lambda0 < 1.336:
        rho_LTB = 1.11 * (1 - 0.278 * lambda0**2)
    else:
        rho_LTB = 1 / lambda0**2
    
    # Effective section modulus for LTB (simplified)
    Wc_ef = effective_props["Wx_efetivo"]  # Conservative
    
    Mx_Rd_LTB = rho_LTB * Wc_ef * fy / gamma_a1
    
    # Distortional buckling resistance (simplified)
    # For U-sections with lips, often not critical compared to LTB
    Mx_Rd_dist = float('inf')
    
    # Final resistance is minimum of all checks
    Mx_Rd = min(Mx_Rd_yield, Mx_Rd_LTB, Mx_Rd_dist)
    My_Rd = min(My_Rd_yield, Mx_Rd_dist)  # No LTB for bending about y-axis
    
    return {
        "Mx_Rd_yield": Mx_Rd_yield,
        "Mx_Rd_LTB": Mx_Rd_LTB,
        "Mx_Rd_dist": Mx_Rd_dist,
        "Mx_Rd": Mx_Rd,
        "My_Rd": My_Rd,
        "Me": Me,
        "lambda0_LTB": lambda0,
        "rho_LTB": rho_LTB
    }

# --- Shear Resistance (NBR 14762 Section 8.4) ---
def calculate_shear_resistance(gross_props, fy):
    """
    Calculate shear resistance according to NBR 14762 Section 8.4
    """
    h = gross_props["bw"] - 2*gross_props["t"]  # Clear web height
    t = gross_props["t"]
    
    # Web slenderness
    h_t_ratio = h / t
    
    # Limits
    limit1 = 1.08 * np.sqrt(E_aço * kv_shear / fy)
    limit2 = 1.4 * np.sqrt(E_aço * kv_shear / fy)
    
    # Shear resistance for web (Vx)
    if h_t_ratio <= limit1:
        Vx_rd = 0.6 * fy * h * t / gamma_a1
    elif h_t_ratio <= limit2:
        Vx_rd = 0.65 * t**2 * np.sqrt(kv_shear * fy * E_aço) / gamma_a1
    else:
        Vx_rd = (0.905 * E_aço * kv_shear * t**3 / h) / gamma_a1
    
    # Shear resistance for flanges (Vy)
    bf_t_ratio = gross_props["bf"] / t
    if bf_t_ratio <= limit1:
        Vy_rd = 0.6 * fy * (2 * gross_props["bf"] * t) / gamma_a1
    elif bf_t_ratio <= limit2:
        Vy_rd = 0.65 * t**2 * np.sqrt(kv_shear * fy * E_aço) / gamma_a1
    else:
        Vy_rd = (0.905 * E_aço * kv_shear * t**3 / gross_props["bf"]) / gamma_a1
    
    return {"Vx_rd": Vx_rd, "Vy_rd": Vy_rd}

# --- Combined Load Interaction (NBR 14762 Section 9) ---
def calculate_interaction_ratios(N_sd, Mx_sd, My_sd, Vx_sd, Vy_sd, 
                               resistances, elastic_loads):
    """
    Calculate interaction ratios according to NBR 14762 Section 9
    """
    # Initialize ratios
    ratio_N_M = 0.0
    ratio_V_V = 0.0
    
    # Axial + Moment interaction
    if N_sd >= 0:  # Compression
        # Equation 9.1 (with second-order effects)
        term_axial = N_sd / resistances["Nc_Rd"] if resistances["Nc_Rd"] > 0 else float('inf')
        
        # Moment amplification factors
        ampl_mx = (1 - N_sd/elastic_loads["Nex"]) if elastic_loads["Nex"] > 0 else float('inf')
        ampl_my = (1 - N_sd/elastic_loads["Ney"]) if elastic_loads["Ney"] > 0 else float('inf')
        
        term_mx = Mx_sd / (ampl_mx * resistances["Mx_Rd"]) if (ampl_mx > 0 and resistances["Mx_Rd"] > 0) else float('inf')
        term_my = My_sd / (ampl_my * resistances["My_Rd"]) if (ampl_my > 0 and resistances["My_Rd"] > 0) else float('inf')
        
        ratio_N_M = term_axial + term_mx + term_my
        
        # Equation 9.2 (without second-order effects)
        ratio_N_M2 = (N_sd/resistances["Nc_Rd"] + 
                      Mx_sd/resistances["Mx_Rd"] + 
                      My_sd/resistances["My_Rd"])
        
        # Use the more critical one
        ratio_N_M = max(ratio_N_M, ratio_N_M2)
    else:  # Tension
        ratio_N_M = (abs(N_sd)/resistances["Nt_Rd"] + 
                    abs(Mx_sd)/resistances["Mx_Rd"] + 
                    abs(My_sd)/resistances["My_Rd"])
    
    # Shear + Moment interaction
    if (Mx_sd != 0 or My_sd != 0 or Vx_sd != 0 or Vy_sd != 0):
        if resistances["Mx_Rd"] > 0:
            ratio_V_V += (Mx_sd/resistances["Mx_Rd"])**2
        if resistances["My_Rd"] > 0:
            ratio_V_V += (My_sd/resistances["My_Rd"])**2
        if resistances["Vx_rd"] > 0:
            ratio_V_V += (Vx_sd/resistances["Vx_rd"])**2
        if resistances["Vy_rd"] > 0:
            ratio_V_V += (Vy_sd/resistances["Vy_rd"])**2
    
    # Overall status
    overall_status = (ratio_N_M <= 1.0) and (ratio_V_V <= 1.0)
    
    return {
        "ratio_N_M": ratio_N_M,
        "ratio_V_V": ratio_V_V,
        "overall_status": overall_status
    }

# --- Main Structural Verification Function ---
def structural_verification_nbr14762(largura, altura, espessura, rm, cm, fy, 
                                   Lx, Ly, Lt, Kx, Ky, Kt, Lb, L_dist,
                                   N_sd, Mx_sd, My_sd, Vx_sd, Vy_sd):
    """
    Main function for structural verification according to NBR 14762
    """
    # 1. Calculate Gross Properties
    gross_props = calculate_gross_properties(largura, altura, espessura, rm, cm)
    if gross_props is None:
        return None
    
    # 2. Calculate Effective Properties
    effective_props = calculate_effective_properties(
        gross_props, N_sd, Mx_sd, My_sd, fy)
    
    # Calculate effective lengths
    le_x = Kx * Lx
    le_y = Ky * Ly
    le_t = Kt * Lt
    
    # 3. Calculate Elastic Buckling Loads
    elastic_loads = calculate_elastic_buckling_loads(gross_props, le_x, le_y, le_t)
    
    # 4. Calculate Compression Resistance
    comp_resistances = calculate_compression_resistance(
        gross_props, effective_props, elastic_loads, fy, L_dist)
    
    # 5. Calculate Bending Resistance
    bending_resistances = calculate_bending_resistance(
        gross_props, effective_props, fy, Lb)
    
    # 6. Calculate Shear Resistance
    shear_resistances = calculate_shear_resistance(gross_props, fy)
    
    # Combine all resistances
    resistances = {**comp_resistances, **bending_resistances, **shear_resistances}
    
    # 7. Calculate Interaction Ratios
    interaction_results = calculate_interaction_ratios(
        N_sd, Mx_sd, My_sd, Vx_sd, Vy_sd,
        resistances, elastic_loads)
    
    # Combine all results
    results = {
        "inputs": {
            "largura": largura, "altura": altura, "espessura": espessura, 
            "rm": rm, "cm": cm, "fy": fy,
            "Lx": Lx, "Ly": Ly, "Lt": Lt, "Lb": Lb, "L_dist": L_dist,
            "Kx": Kx, "Ky": Ky, "Kt": Kt,
            "N_sd": N_sd, "Mx_sd": Mx_sd, "My_sd": My_sd, 
            "Vx_sd": Vx_sd, "Vy_sd": Vy_sd
        },
        "calculated_lengths": {"le_x": le_x, "le_y": le_y, "le_t": le_t},
        "gross_properties": gross_props,
        "effective_properties": effective_props,
        "elastic_buckling_loads": elastic_loads,
        "resistances": resistances,
        "interaction": interaction_results
    }
    
    return results

# --- Streamlit App Interface ---
def main():
    st.set_page_config(page_title="Verificação de Perfil U Enrijecido (NBR 14762)", layout="centered")
    st.title("Verificação de Perfil U Enrijecido Conforme NBR 14762")
    
    st.markdown("""
    <style>
        .stButton>button {border-radius: 12px; background-color: #4a90e2; color: white; font-size: 16px;}
        .stTextInput>div>div>input {border-radius: 8px;}
        .stNumberInput>div>div>input {border-radius: 8px;}
    </style>
    """, unsafe_allow_html=True)
    
    st.sidebar.header("Parâmetros do Perfil")
    with st.sidebar:
        largura = st.number_input("Largura da aba (bf, mm)", value=50.0, min_value=0.1, format="%.1f")
        altura = st.number_input("Altura da alma (h, mm)", value=100.0, min_value=0.1, format="%.1f")
        espessura = st.number_input("Espessura (t, mm)", value=2.0, min_value=0.1, format="%.2f")
        rm = st.number_input("Raio interno (rm, mm)", value=4.0, min_value=0.0, format="%.2f")
        cm = st.number_input("Comprimento do lábio (cm, mm)", value=15.0, min_value=0.0, format="%.1f")
        fy = st.selectbox("Resistência do aço (fy, MPa)", [230, 250, 300, 350, 420], index=1)
    
    st.sidebar.header("Comprimentos e Coeficientes")
    with st.sidebar:
        Lx = st.number_input("Lx (mm) - Flambagem em X", value=3000.0, min_value=1.0, format="%.1f")
        Ly = st.number_input("Ly (mm) - Flambagem em Y", value=3000.0, min_value=1.0, format="%.1f")
        Lt = st.number_input("Lt (mm) - Flambagem torsional", value=3000.0, min_value=1.0, format="%.1f")
        Lb = st.number_input("Lb (mm) - FLT", value=3000.0, min_value=1.0, format="%.1f")
        L_dist = st.number_input("L_dist (mm) - Distorção", value=3000.0, min_value=1.0, format="%.1f")
        
        Kx = st.slider("Kx - Coef. flambagem X", 0.5, 2.0, value=1.0, step=0.1)
        Ky = st.slider("Ky - Coef. flambagem Y", 0.5, 2.0, value=1.0, step=0.1)
        Kt = st.slider("Kt - Coef. flambagem torsional", 0.5, 2.0, value=1.0, step=0.1)
    
    st.sidebar.header("Solicitações de Cálculo")
    with st.sidebar:
        N_sd = st.number_input("Força axial (N_sd, N)", value=50000.0, format="%.1f")
        Mx_sd = st.number_input("Momento em X (Mx_sd, N.mm)", value=10000000.0, format="%.1f")
        My_sd = st.number_input("Momento em Y (My_sd, N.mm)", value=5000000.0, format="%.1f")
        Vx_sd = st.number_input("Cortante em X (Vx_sd, N)", value=20000.0, format="%.1f")
        Vy_sd = st.number_input("Cortante em Y (Vy_sd, N)", value=15000.0, format="%.1f")
    
    if st.button("Executar Verificação NBR 14762"):
        with st.spinner("Calculando..."):
            results = structural_verification_nbr14762(
                largura, altura, espessura, rm, cm, fy,
                Lx, Ly, Lt, Kx, Ky, Kt, Lb, L_dist,
                N_sd, Mx_sd, My_sd, Vx_sd, Vy_sd)
        
        if results is None:
            st.error("Erro na verificação. Verifique os dados de entrada.")
            return
        
        # Display Results
        st.subheader("Resultados da Verificação")
        
        # Gross Properties
        with st.expander("Propriedades Geométricas Brutas"):
            gp = results["gross_properties"]
            st.write(f"Área Bruta (A): {gp['A_bruta']:.2f} mm²")
            st.write(f"Inércia Ix: {gp['Ix_bruta']:.2f} mm⁴")
            st.write(f"Inércia Iy: {gp['Iy_bruta']:.2f} mm⁴")
            st.write(f"Módulo Wx: {gp['Wx_bruto']:.2f} mm³")
            st.write(f"Módulo Wy: {gp['Wy_bruto']:.2f} mm³")
            st.write(f"Raio de giração rx: {gp['rx_bruto']:.2f} mm")
            st.write(f"Raio de giração ry: {gp['ry_bruto']:.2f} mm")
            st.write(f"Constante de torção It: {gp['It_bruta']:.2f} mm⁴")
            st.write(f"Constante de empenamento Cw: {gp['Cw']:.2f} mm⁶")
            st.write(f"Centro de cisalhamento x0: {gp['x0']:.2f} mm")
            st.write(f"Raio polar r0: {gp['r0']:.2f} mm")
        
        # Effective Properties
        with st.expander("Propriedades Efetivas"):
            ep = results["effective_properties"]
            st.write(f"Área Efetiva (A_ef): {ep['A_efetiva']:.2f} mm²")
            st.write(f"Largura efetiva da alma: {ep['be_web']:.2f} mm")
            st.write(f"Largura efetiva da mesa: {ep['be_flange']:.2f} mm")
            st.write(f"Largura efetiva do lábio: {ep['be_lip']:.2f} mm")
            st.write(f"Módulo efetivo Wx: {ep['Wx_efetivo']:.2f} mm³")
            st.write(f"Módulo efetivo Wy: {ep['Wy_efetivo']:.2f} mm³")
            st.write(f"Deslocamento do CG: {ep['CG_shift_ef']:.2f} mm")
        
        # Resistances
        with st.expander("Resistências de Cálculo"):
            res = results["resistances"]
            st.write("**Compressão:**")
            st.write(f"Resistência ao escoamento (Ny_Rd): {res['Ny_Rd']/1000:.2f} kN")
            st.write(f"Resistência à flambagem global (Nf_Rd): {res['Nf_Rd']/1000:.2f} kN")
            st.write(f"Resistência à flambagem distorcional (Nd_Rd): {res['Nd_Rd']/1000:.2f} kN" if res['Nd_Rd'] != float('inf') else "Resistência à flambagem distorcional (Nd_Rd): Não crítica")
            st.write(f"Resistência à compressão (Nc_Rd): {res['Nc_Rd']/1000:.2f} kN")
            st.write(f"Resistência à tração (Nt_Rd): {res['Nt_Rd']/1000:.2f} kN")
            
            st.write("\n**Flexão:**")
            st.write(f"Resistência ao escoamento (Mx_Rd): {res['Mx_Rd_yield']/1e6:.2f} kN.m")
            st.write(f"Resistência à FLT (Mx_Rd_LTB): {res['Mx_Rd_LTB']/1e6:.2f} kN.m")
            st.write(f"Resistência à distorção (Mx_Rd_dist): {res['Mx_Rd_dist']/1e6:.2f} kN.m" if res['Mx_Rd_dist'] != float('inf') else "Resistência à distorção (Mx_Rd_dist): Não crítica")
            st.write(f"Resistência final (Mx_Rd): {res['Mx_Rd']/1e6:.2f} kN.m")
            st.write(f"Resistência em Y (My_Rd): {res['My_Rd']/1e6:.2f} kN.m")
            
            st.write("\n**Cisalhamento:**")
            st.write(f"Resistência ao cisalhamento em X (Vx_rd): {res['Vx_rd']/1000:.2f} kN")
            st.write(f"Resistência ao cisalhamento em Y (Vy_rd): {res['Vy_rd']/1000:.2f} kN")
        
        # Interaction Checks
        with st.expander("Verificações de Interação"):
            inter = results["interaction"]
            st.write(f"Razão de interação (Axial + Flexão): {inter['ratio_N_M']:.3f}")
            st.write(f"Razão de interação (Cisalhamento + Flexão): {inter['ratio_V_V']:.3f}")
            
            if inter["overall_status"]:
                st.success("✅ PERFIL VERIFICADO COM SUCESSO")
            else:
                st.error("❌ PERFIL NÃO VERIFICADO - RAZÕES DE INTERAÇÃO EXCEDIDAS")
        
        # Elastic Buckling Loads
        with st.expander("Cargas Críticas de Flambagem Elástica"):
            el = results["elastic_buckling_loads"]
            st.write(f"Nex (Flambagem por flexão em X): {el['Nex']/1000:.2f} kN")
            st.write(f"Ney (Flambagem por flexão em Y): {el['Ney']/1000:.2f} kN")
            st.write(f"Net (Flambagem por torção): {el['Net']/1000:.2f} kN")
            st.write(f"Next (Flambagem por flexo-torção): {el['Next']/1000:.2f} kN")
            st.write(f"Ne (Carga crítica de flambagem): {el['Ne']/1000:.2f} kN")
        
        # Parameters
        with st.expander("Parâmetros de Flambagem"):
            st.write(f"Índice de esbeltez reduzido (λ₀): {results['resistances']['lambda0']:.3f}")
            st.write(f"Fator de redução (ρ): {results['resistances']['rho']:.3f}")
            if results['resistances']['lambda_dist'] != float('inf'):
                st.write(f"Índice de esbeltez distorcional (λ_dist): {results['resistances']['lambda_dist']:.3f}")
                st.write(f"Tensão crítica distorcional (σ_dist): {results['resistances']['sigma_dist']:.2f} MPa")

if __name__ == "__main__":
    main()
