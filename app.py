import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Tablero de Registros de Reclutamiento", layout="wide")

st.title("📊 Tablero de Registros de Reclutamiento")
st.markdown("Visualización interactiva de la productividad diaria y mensual por reclutador.")

@st.cache_data
def load_data():
    file_name = "frecuencia_registros_12_meses.xlsx"
    df_resumen = pd.read_excel(file_name, sheet_name="Resumen_12_Meses")
    df_detalle = pd.read_excel(file_name, sheet_name="Detalle_Diario")
    return df_resumen, df_detalle

try:
    df_resumen, df_detalle = load_data()
    st.success("¡Datos cargados exitosamente desde el archivo Excel!")
    
    # Filtros en la barra lateral
    st.sidebar.header("Filtros")
    anos_disponibles = sorted(df_resumen["anio"].unique())
    anio_seleccionado = st.sidebar.selectbox("Seleccione el Año (Resumen)", anos_disponibles)
    
    df_res_filtered = df_resumen[df_resumen["anio"] == anio_seleccionado]
    
    # Título dinámico corregido con el año seleccionado
    st.subheader(f"Resumen Anual de Registros ({anio_seleccionado})")
    st.dataframe(df_res_filtered, use_container_width=True)
    
    # Gráfico de barras de resumen anual
    fig = px.bar(
        df_res_filtered, 
        x="reclutador", 
        y="Total_Anual", 
        title=f"Total de Registros por Reclutador en {anio_seleccionado}",
        labels={"reclutador": "Reclutador", "Total_Anual": "Total Anual de Registros"},
        color="reclutador"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # --- SECCIÓN: DETALLE DIARIO INTERACTIVO (ESTILO YAHOO FINANCE) ---
    st.subheader("Seguimiento Diario de Registros")
    
    reclutadores = sorted(df_detalle["reclutador"].unique())
    rec_seleccionado = st.selectbox("Seleccione Reclutador para Detalle Diario", reclutadores)
    
    # Filtrar por reclutador seleccionado
    df_rec = df_detalle[df_detalle["reclutador"] == rec_seleccionado].copy()
    
    if not df_rec.empty:
        # Construir columna de fecha completa usando rename para asegurar el formato de datetime
        df_rec["fecha"] = pd.to_datetime(
            df_rec[["anio", "mes", "dia"]].rename(columns={"anio": "year", "mes": "month", "dia": "day"})
        )
        df_rec = df_rec.sort_values("fecha")
        
        # Calcular media móvil de 7 días para suavizar la curva
        df_rec["Media_Movil_7D"] = df_rec["registros_nuevos"].rolling(window=7, min_periods=1).mean()
        
        # Crear figura con go.Figure
        fig_fin = go.Figure()
        
        # Línea y puntos de Registros Nuevos
        fig_fin.add_trace(go.Scatter(
            x=df_rec["fecha"],
            y=df_rec["registros_nuevos"],
            mode="lines+markers",
            name="Registros Nuevos",
            line=dict(color="forestgreen", width=2),
            marker=dict(size=5)
        ))
        
        # Línea de Media Móvil (7D)
        fig_fin.add_trace(go.Scatter(
            x=df_rec["fecha"],
            y=df_rec["Media_Movil_7D"],
            mode="lines",
            name="Media Móvil (7D)",
            line=dict(color="royalblue", width=2, dash="dot")
        ))
        
        # Configurar interactividad financiera (Rangeselector y RangeSlider)
        fig_fin.update_layout(
            title=f"Seguimiento Diario de Registros: {rec_seleccionado}",
            xaxis_title="Fecha",
            yaxis_title="Cantidad de Registros",
            hovermode="x unified",
            template="plotly_white",
            height=520,
            xaxis=dict(
                rangeselector=dict(
                    buttons=list([
                        dict(count=1, label="1M", step="month", stepmode="backward"),
                        dict(count=6, label="6M", step="month", stepmode="backward"),
                        dict(count=1, label="1A", step="year", stepmode="backward"),
                        dict(step="all", label="Todo")
                    ])
                ),
                rangeslider=dict(visible=True),
                type="date"
            )
        )
        
        st.plotly_chart(fig_fin, use_container_width=True)
    else:
        st.info("No hay registros diarios para esta selección.")

except Exception as e:
    st.error(f"No se pudo cargar el archivo Excel. Verifique que esté en el mismo directorio. Detalle del error: {e}")