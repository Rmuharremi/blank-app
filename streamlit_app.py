import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

st.title("Foundation Footing Visualizer with Soil Pressure (kN/m)")

# Input parameters in sidebar
with st.sidebar:
    st.header("Structural Inputs")
    B = st.number_input("Footing width (B) [m]", min_value=0.1, value=2.0)
    L = st.number_input("Footing depth (L) [m]", min_value=0.1, value=2.0)
    H = st.number_input("Footing height (H) [m]", min_value=0.1, value=0.5)
    a = st.number_input("Column width (a) [m]", min_value=0.1, value=0.4)
    b = st.number_input("Column height (b) [m]", min_value=0.1, value=0.6)
    
    st.header("Loading Inputs")
    N = st.number_input("Normal force (N) [kN]", min_value=0.1, value=80.0)
    M = st.number_input("Moment (M) [kN·m]", value=34.0)

# Calculate soil pressure distribution in kN/m
e = M / N if N != 0 else 0
q_max = q_min = 0
contact_length = B

if N != 0:
    if abs(e) > B/6:
        st.warning(f"Eccentricity (e = {e:.2f}m) exceeds B/6 ({B/6:.2f}m)")
        effective_length = 3*(B/2 - abs(e)) if e > 0 else 3*(B/2 + abs(e))
        q_max = (2*N)/(effective_length)
        q_min = 0
        contact_length = effective_length
    else:
        q_avg = N/B
        q_max = q_avg*(1 + 6*abs(e)/B)
        q_min = q_avg*(1 - 6*abs(e)/B)
        q_max, q_min = (q_max, q_min) if e >=0 else (q_min, q_max)

# Create figure with adjusted size
fig, ax = plt.subplots(figsize=(12, 10))

# Draw footing
footing = plt.Rectangle((0, 0), B, H, 
                       edgecolor='#2B5F85', facecolor='#7EB6FF', 
                       linewidth=2, label='Footing')
ax.add_patch(footing)

# Draw column
column_x = (B - a)/2
column_top = H + b
column = plt.Rectangle((column_x, H), a, b, 
                      edgecolor='#852B2B', facecolor='#FF7E7E', 
                      linewidth=2, label='Column')
ax.add_patch(column)

# Add midline
ax.axvline(B/2, color='red', linestyle='--', linewidth=1.5, label='Midline')

# Draw soil pressure distribution
pressure_depth = 0.3 * H  # Increased pressure depth
y_base = -pressure_depth

if N != 0:
    if abs(e) > B/6:
        x = [B-contact_length, B] if e > 0 else [0, contact_length]
        q_values = [0, q_max]
    else:
        x = [0, B]
        q_values = [q_min, q_max]
    
    # Plot pressure arrows
    for xi, qi in zip(x, q_values):
        ax.arrow(xi, y_base, 0, -qi/50, head_width=0.1, head_length=0.1, 
                fc='darkgreen', ec='darkgreen', linewidth=1)
    
    # Plot pressure distribution line
    ax.plot(x, [y_base]*2, 'darkgreen', linewidth=2)
    ax.plot(x, [y_base - qv/50 for qv in q_values], '--', color='darkgreen', alpha=0.5)
    
    # Fill pressure area
    ax.fill_between(x, 
                   [y_base]*2, 
                   [y_base - qv/50 for qv in q_values], 
                   color='green', alpha=0.1)
    
    # Add pressure labels
    if abs(e) > B/6:
        if e > 0:
            ax.text(B, y_base - (q_max/100), 
                   f"{q_max:.1f} kN/m", ha='right', va='top', color='darkgreen')
            ax.text(B-contact_length, y_base, 
                   "0.0 kN/m", ha='left', va='top', color='darkgreen')
        else:
            ax.text(0, y_base - (q_max/100), 
                   f"{q_max:.1f} kN/m", ha='left', va='top', color='darkgreen')
            ax.text(contact_length, y_base, 
                   "0.0 kN/m", ha='right', va='top', color='darkgreen')
    else:
        ax.text(0, y_base - (q_min/100), 
               f"{q_min:.1f} kN/m", ha='left', va='top', color='darkgreen')
        ax.text(B, y_base - (q_max/100), 
               f"{q_max:.1f} kN/m", ha='right', va='top', color='darkgreen')

    # Calculate reaction force R and its position
    if abs(e) > B/6:
        if e > 0:
            R = 0.5 * (B - B/2) * q_max
            #qmid=(q_max/contact_length*(contact_length-B/2))
            x_R = B/2 + B/2-(B/6*((2*(q_max/contact_length*(contact_length-B/2))+q_max)/((q_max/contact_length*(contact_length-B/2))+q_max)))
            #(h/3*((2a+b)/(a+b)))
        else:
            R = 0.5 * (B/2 - 0) * q_max
            x_R = B/2 - (B/2)/3
    else:
        q_mid = (q_max + q_min)/2
        R = 0.5 * (q_mid + q_max) * (B/2)
        x_R = B/2 + B/2-(B/2)*(2*q_mid + q_max)/(3*(q_mid + q_max))

    # Draw reaction force R below footing
    r_arrow_base = y_base - 0.7  # Position below pressure area
    ax.arrow(x_R, r_arrow_base, 0, 0.5, head_width=0.05, head_length=0.1,
             fc='purple', ec='purple', linewidth=2, label='Reaction R')
    ax.text(x_R + 0.3, r_arrow_base + 0.3, f"R = {R:.1f} kN", 
            ha='center', va='top', color='purple')

# Draw N and M arrows
if N != 0:
    # Normal force N (downward arrow)
    n_arrow_start = column_top + 0.2
    ax.arrow(column_x + a/2, n_arrow_start, 0, -0.3, 
             head_width=0.15, head_length=0.1, fc='blue', ec='blue')
    ax.text(column_x + a/2, n_arrow_start - 0.35, f"N = {N} kN", 
            ha='center', va='top', color='blue')
    
    # Moment M (curved arrow)
    m_sign = np.sign(M)
    arc_radius = 0.4
    ax.annotate('', xy=(column_x  + m_sign*arc_radius, column_top + 0.3),
                xytext=(column_x , column_top + 0.3),
                arrowprops=dict(arrowstyle='->', color='orange', 
                                connectionstyle=f"arc3,rad={-m_sign*0.5}",
                                linewidth=2))
    ax.text(column_x + m_sign*0.45, column_top + 0.3, 
            f"M = {M} kN·m", ha='left' if m_sign > 0 else 'right', color='orange')

# Configure plot with dynamic scaling
ax.set_xlim(-0.2, B+0.2)
max_pressure_height = max(q_max/50 if N !=0 else 1, 1)
ax.set_ylim(-max_pressure_height - 0.5, H + b + 0.5)
ax.set_xlabel('Width (m)')
ax.set_ylabel('Height (m)')
ax.set_title(f"Section View (B = {B}m, L = {L}m)\nSoil Pressure Distribution @ {N} kN")
ax.grid(True, linestyle='--', alpha=0.7)
ax.set_aspect('equal')
ax.legend(loc='upper right')

# Verification calculation
if N != 0:
    if abs(e) > B/6:
        area = 0.5 * contact_length * q_max
    else:
        area = 0.5 * (q_max + q_min) * B
    
    st.markdown(f"""
    **Verification:**
    - Total soil reaction (Area × 1m): **{area:.2f} kN**
    - Applied normal force: **{N:.2f} kN**
    - Difference: **{(abs(area - N)/N * 100 if N !=0 else 0):.2f}%**
    """)

st.pyplot(fig)

# Explanations
st.markdown("""
**Visualization Notes:**
- Red dashed line: Midline of footing
- Blue downward arrow: Normal force (N)
- Orange curved arrow: Moment (M) direction
- Purple arrow: Resultant soil reaction (R)
- Green area: Soil pressure distribution (kN/m)
- All values shown in actual scale relationship
""")