
import streamlit as st
import pandas as pd
import altair as alt
import io

st.set_page_config(page_title="Evaluador Visual de Complejidad Cloud", layout="wide")

st.markdown("""
# ☁️ Evaluador Visual de Complejidad Cloud
_Convierte tu arquitectura tecnológica en una evaluación profesional en segundos._

---

💡 **¿Cómo funciona?**
1. Ingresa las cantidades por tecnología.
2. Se asigna automáticamente el **nivel de complejidad** (1-3).
3. Visualiza el **rango asignado**, el costo base, el precio al cliente (con margen), y el puntaje.
4. Exporta a Excel con todo el detalle para presentar o cotizar.

""")

tecnologias = [
    "Application Discovery Services", "Application Services", "Artificial Intelligence",
    "Artificial Intelligence / Machine Learning", "Automated Cloud Management Service",
    "Big Data", "Business Productivity", "Compute", "Database", "Developer Tools",
    "Disaster Recovery Services", "Game Development", "Hybrid Cloud",
    "Internet of Things", "Management Tools", "Migration Services", "Mobile Services",
    "Networking", "Robotics Development", "Security & Identity, Compliance",
    "Software MarketPlace", "Storage", "Tomcat", "WebLogic", "Data Guard"
]

# Clasificación de niveles
nivel_por_tecnologia = {
    1: ["Storage", "Mobile Services", "Developer Tools", "Application Discovery Services", "Software MarketPlace", "Internet of Things"],
    2: ["Compute", "Networking", "Hybrid Cloud", "Application Services", "Business Productivity", "Migration Services"],
    3: ["Database", "WebLogic", "Tomcat", "Data Guard", "Big Data", "Artificial Intelligence",
        "Security & Identity, Compliance", "Disaster Recovery Services", "Management Tools",
        "Automated Cloud Management Service", "Development & Testing", "Robotics Development"]
}
rango_etiquetas = {
    1: "🟢 Nivel 1 - Bajo",
    2: "🟡 Nivel 2 - Medio",
    3: "🔴 Nivel 3 - Alto"
}
precios = {1: 50, 2: 60, 3: 120}

# Entrada del usuario
df = pd.DataFrame({"Tecnología": tecnologias, "Cantidad": [0]*len(tecnologias)})
df = st.data_editor(df, use_container_width=True, num_rows="fixed")

# Enriquecer tabla con cálculos
df["Nivel"] = df["Tecnología"].apply(
    lambda x: 3 if x in nivel_por_tecnologia[3] else 2 if x in nivel_por_tecnologia[2] else 1
)
df["Rango"] = df["Nivel"].map(rango_etiquetas)
df["Precio Base"] = df["Nivel"].map(precios)
df["Puntaje"] = df["Cantidad"] * df["Nivel"]
df["Costo Mensual"] = df["Cantidad"] * df["Precio Base"]
df["Precio Cliente Mensual"] = df["Costo Mensual"] * 1.4
df["Margen Mensual"] = df["Precio Cliente Mensual"] - df["Costo Mensual"]

# Cálculos finales
puntaje_total = df["Puntaje"].sum()
costo_mensual = df["Costo Mensual"].sum()
precio_cliente_mensual = df["Precio Cliente Mensual"].sum()
margen_mensual = df["Margen Mensual"].sum()
costo_anual = costo_mensual * 12
precio_cliente_anual = precio_cliente_mensual * 12
margen_anual = precio_cliente_anual - costo_anual

nivel_global = (
    "🟢 Nivel 1 - Bajo" if puntaje_total <= 30 else
    "🟡 Nivel 2 - Medio" if puntaje_total <= 60 else
    "🔴 Nivel 3 - Alto"
)

st.markdown("## 📊 Resumen Global")
col1, col2, col3 = st.columns(3)
col1.metric("Puntaje Total", puntaje_total)
col2.metric("Nivel Global", nivel_global)
col3.metric("Precio Cliente Mensual", f"${precio_cliente_mensual:,.2f}")

st.markdown("### 📋 Tabla Detallada")
st.dataframe(df[["Tecnología", "Cantidad", "Rango", "Puntaje", "Precio Cliente Mensual"]], use_container_width=True)


color_nivel = (
    "#d1f0d1" if nivel_global.startswith("🟢") else
    "#fff5cc" if nivel_global.startswith("🟡") else
    "#ffd6cc"
)
st.markdown(f"""
    <style>
    .main {{
        background-color: {color_nivel};
    }}
    </style>
""", unsafe_allow_html=True)

st.markdown("### 💰 Desglose Financiero")
st.table(pd.DataFrame({
    "": ["Costo Mensual", "Costo Anual"],
    "Puntaje Total": [puntaje_total, ""],
    "Costo": [f"${costo_mensual:,.2f}", f"${costo_anual:,.2f}"],
    "Margen": ["40%", "40%"],
    "Precio al Cliente": [f"${precio_cliente_mensual:,.2f}", f"${precio_cliente_anual:,.2f}"],
    "Utilidad": [f"${margen_mensual:,.2f}", f"${margen_anual:,.2f}"]
}))

st.markdown("### 📈 Visualización Interactiva")
chart = alt.Chart(df[df["Cantidad"] > 0]).mark_bar().encode(
    x="Tecnología:N",
    y="Precio Cliente Mensual:Q",
    color="Rango:N",
    tooltip=["Cantidad", "Nivel", "Precio Cliente Mensual"]
).properties(width=900, height=400)

st.altair_chart(chart, use_container_width=True)

st.markdown("### 📥 Exportar Resultados")
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
    df.to_excel(writer, index=False, sheet_name="Evaluación por Tecnología")
    pd.DataFrame({
        "Clasificación según Puntaje Total": [
            "0 – 30: Nivel 1 - Bajo (Monitoreo y respuesta reactiva)",
            "31 – 60: Nivel 2 - Medio (Nivel 1 + Tareas operativas, actualizaciones, respaldos)",
            "61 o más: Nivel 3 - Alto (Nivel 1 y 2 + Gestión proactiva, hardening, tuning, DR, etc.)"
        ]
    }).to_excel(writer, index=False, sheet_name="Justificación")
    df.to_excel(writer, index=False, sheet_name="Evaluación por Tecnología")
    pd.DataFrame({
        "Clasificación por Puntaje Total": [
            "0 – 30: Nivel 1 - Bajo - Soporte reactivo",
            "31 – 60: Nivel 2 - Medio - Backups, tareas operativas",
            "61 o más: Nivel 3 - Alto - DR, hardening, tuning"
        ]
    }).to_excel(writer, index=False, sheet_name="Justificación de Niveles")

st.download_button("Descargar Excel", buffer.getvalue(), file_name="evaluacion_cloud_final.xlsx")


st.markdown("""
### 🧾 Clasificación según Puntaje Total:

- **0 – 30**: Nivel 1 - Bajo (Monitoreo y respuesta reactiva)  
- **31 – 60**: Nivel 2 - Medio (Nivel 1 + Tareas operativas, actualizaciones, respaldos)  
- **61 o más**: Nivel 3 - Alto (Nivel 1 y 2 + Gestión proactiva, hardening, tuning, DR, etc.)
""")



with st.expander("📘 ¿Cómo se clasifica el nivel? (ver detalles)"):
    st.markdown("""
    **Clasificación según Puntaje Total:**

    - **0 – 30**: Nivel 1 - Bajo  
      *Monitoreo y respuesta reactiva*

    - **31 – 60**: Nivel 2 - Medio  
      *Nivel 1 + Tareas operativas, actualizaciones, respaldos*

    - **61 o más**: Nivel 3 - Alto  
      *Nivel 1 y 2 + Gestión proactiva, hardening, tuning, DR, etc.*
    """)



with st.expander("📘 ¿Cómo se clasifica el nivel? (ver detalles)"):
    st.markdown("""
    **Clasificación según Puntaje Total:**

    - **0 – 30**: Nivel 1 - Bajo  
      *Monitoreo y respuesta reactiva*

    - **31 – 60**: Nivel 2 - Medio  
      *Nivel 1 + Tareas operativas, actualizaciones, respaldos*

    - **61 o más**: Nivel 3 - Alto  
      *Nivel 1 y 2 + Gestión proactiva, hardening, tuning, DR, etc.*
    """)
