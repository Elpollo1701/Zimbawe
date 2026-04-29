"""
╔══════════════════════════════════════════════════════════╗
║         ZIMBAWE BEAUTY - SISTEMA DE INVENTARIO           ║
║         Stack: Streamlit + Google Sheets                  ║
║         Mobile-First | Gratis | Sin servidor propio       ║
╚══════════════════════════════════════════════════════════╝

PARA CORRER LOCALMENTE:
  streamlit run app.py

PARA DESPLEGAR:
  1. Sube este repo a GitHub
  2. Conecta en share.streamlit.io
  3. Agrega tus secrets (ver GUIA.md)
"""

import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# ══════════════════════════════════════════════════
#  CONFIGURACIÓN DE PÁGINA (siempre va primero)
# ══════════════════════════════════════════════════
st.set_page_config(
    page_title="💄 Zimbawe Beauty",
    page_icon="💄",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════
#  ESTILOS CSS — MOBILE-FIRST & PALETA BEAUTY
# ══════════════════════════════════════════════════
st.markdown("""
<style>
/* ---- Variables de color ---- */
:root {
    --rosa:     #E91E8C;
    --rosa-claro: #F8BBD9;
    --dorado:   #C8973A;
    --fondo:    #FFF9FC;
    --texto:    #2D1B2E;
    --gris:     #6B5672;
    --verde:    #27AE60;
    --rojo:     #E74C3C;
    --radio:    14px;
}

/* ---- Fondo general ---- */
.stApp { background: var(--fondo); }
.block-container { padding: 1rem 1rem 4rem; max-width: 700px; }

/* ---- Header personalizado ---- */
.brand-header {
    background: linear-gradient(135deg, #E91E8C 0%, #9C27B0 100%);
    border-radius: var(--radio);
    padding: 1.2rem 1.5rem;
    text-align: center;
    margin-bottom: 1.2rem;
    box-shadow: 0 4px 20px rgba(233,30,140,0.3);
}
.brand-header h1 {
    color: white;
    font-size: 1.8rem;
    margin: 0;
    letter-spacing: 1px;
}
.brand-header p {
    color: rgba(255,255,255,0.85);
    margin: 0.2rem 0 0;
    font-size: 0.9rem;
}

/* ---- Tabs de navegación grandes ---- */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background: white;
    border-radius: var(--radio);
    padding: 6px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px !important;
    padding: 0.6rem 1rem !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    color: var(--gris) !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #E91E8C, #9C27B0) !important;
    color: white !important;
}

/* ---- Botones grandes (mobile-friendly) ---- */
.stButton > button {
    width: 100%;
    min-height: 3rem;
    font-size: 1rem;
    font-weight: 700;
    border-radius: var(--radio);
    border: none;
    background: linear-gradient(135deg, #E91E8C, #9C27B0);
    color: white;
    letter-spacing: 0.5px;
    transition: all 0.2s;
    box-shadow: 0 3px 12px rgba(233,30,140,0.35);
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 5px 18px rgba(233,30,140,0.45);
}

/* ---- Botones secundarios ---- */
[data-testid="baseButton-secondary"] > button {
    background: white !important;
    color: var(--rosa) !important;
    border: 2px solid var(--rosa) !important;
    box-shadow: none !important;
}

/* ---- Inputs grandes ---- */
.stTextInput input, .stNumberInput input, .stSelectbox select {
    font-size: 1.05rem !important;
    padding: 0.6rem 0.8rem !important;
    border-radius: 10px !important;
    border: 2px solid #EDD9F0 !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color: var(--rosa) !important;
}

/* ---- Tarjetas de métricas ---- */
.metric-card {
    background: white;
    border-radius: var(--radio);
    padding: 1rem;
    text-align: center;
    box-shadow: 0 2px 10px rgba(0,0,0,0.07);
    border-left: 4px solid var(--rosa);
}
.metric-card .num { font-size: 2rem; font-weight: 800; color: var(--rosa); }
.metric-card .label { font-size: 0.8rem; color: var(--gris); font-weight: 600; text-transform: uppercase; }

/* ---- Badge de stock ---- */
.stock-ok   { background:#d4edda; color:#155724; padding:3px 10px; border-radius:20px; font-weight:700; font-size:0.85rem; }
.stock-low  { background:#fff3cd; color:#856404; padding:3px 10px; border-radius:20px; font-weight:700; font-size:0.85rem; }
.stock-zero { background:#f8d7da; color:#721c24; padding:3px 10px; border-radius:20px; font-weight:700; font-size:0.85rem; }

/* ---- Alertas personalizadas ---- */
.alerta-ok  { background:#d1f2eb; color:#0a6b4c; border-radius:10px; padding:0.8rem 1rem; margin:0.5rem 0; font-weight:600; }
.alerta-err { background:#f8d7da; color:#721c24; border-radius:10px; padding:0.8rem 1rem; margin:0.5rem 0; font-weight:600; }

/* ---- Tabla responsive ---- */
.stDataFrame { border-radius: var(--radio); overflow: hidden; }

/* ---- Separadores ---- */
.separador { border: none; border-top: 2px dashed #EDD9F0; margin: 1.2rem 0; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════
#  CONSTANTES
# ══════════════════════════════════════════════════
COLUMNAS = ["Producto", "Categoría", "Stock", "Precio (Bs)", "Última Actualización"]
CATEGORIAS = [
    "💋 Labial", "🌸 Base/Corrector", "💅 Esmalte",
    "👁️ Sombra/Delineador", "🧴 Tinte/Coloración",
    "✨ Cuidado Facial", "🛁 Cuidado Corporal", "🌿 Cabello",
    "💎 Perfumería", "🎨 Maquillaje Varios"
]
STOCK_ALERTA = 5   # Unidades mínimas antes de alerta amarilla

# ══════════════════════════════════════════════════
#  CONEXIÓN A GOOGLE SHEETS
# ══════════════════════════════════════════════════
@st.cache_resource(ttl=30)  # Refresca conexión cada 30 segundos
def get_connection():
    """Retorna la conexión activa a Google Sheets."""
    return st.connection("gsheets", type=GSheetsConnection)


def cargar_datos(conn) -> pd.DataFrame:
    """Lee la hoja de cálculo y devuelve un DataFrame limpio."""
    try:
        df = conn.read(
            worksheet="Inventario",
            usecols=list(range(len(COLUMNAS))),
            ttl=10,  # segundos de caché para esta lectura
        )
        # Limpiar filas completamente vacías
        df = df.dropna(subset=["Producto"])
        df = df[df["Producto"].astype(str).str.strip() != ""]

        # Asegurar tipos correctos
        df["Stock"] = pd.to_numeric(df["Stock"], errors="coerce").fillna(0).astype(int)
        df["Precio (Bs)"] = pd.to_numeric(df["Precio (Bs)"], errors="coerce").fillna(0.0)

        return df.reset_index(drop=True)

    except Exception as e:
        st.error(f"⚠️ Error al leer Google Sheets: {e}")
        # Retorna DataFrame vacío con estructura correcta si falla
        return pd.DataFrame(columns=COLUMNAS)


def guardar_datos(conn, df: pd.DataFrame) -> bool:
    """Escribe el DataFrame completo de vuelta a la hoja."""
    try:
        conn.update(
            worksheet="Inventario",
            data=df,
        )
        # Limpiar caché para forzar recarga
        st.cache_resource.clear()
        return True
    except Exception as e:
        st.error(f"⚠️ Error al guardar: {e}")
        return False


# ══════════════════════════════════════════════════
#  HEADER DE MARCA
# ══════════════════════════════════════════════════
st.markdown("""
<div class="brand-header">
    <h1>💄 Zimbawe Beauty</h1>
    <p>Sistema de Inventario · Rápido · Desde cualquier lugar</p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════
#  CARGAR DATOS (una sola vez por sesión / rerun)
# ══════════════════════════════════════════════════
conn = get_connection()
df_inventario = cargar_datos(conn)

# ══════════════════════════════════════════════════
#  MÉTRICAS RÁPIDAS (siempre visibles arriba)
# ══════════════════════════════════════════════════
total_productos = len(df_inventario)
sin_stock = int((df_inventario["Stock"] == 0).sum()) if total_productos > 0 else 0
stock_bajo = int(((df_inventario["Stock"] > 0) & (df_inventario["Stock"] <= STOCK_ALERTA)).sum()) if total_productos > 0 else 0

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="num">{total_productos}</div>
        <div class="label">Productos</div>
    </div>""", unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="metric-card" style="border-color:#E67E22;">
        <div class="num" style="color:#E67E22;">{stock_bajo}</div>
        <div class="label">Stock Bajo</div>
    </div>""", unsafe_allow_html=True)
with col3:
    st.markdown(f"""
    <div class="metric-card" style="border-color:#E74C3C;">
        <div class="num" style="color:#E74C3C;">{sin_stock}</div>
        <div class="label">Sin Stock</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<hr class='separador'>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════
#  NAVEGACIÓN POR TABS
# ══════════════════════════════════════════════════
tab_consulta, tab_ingreso, tab_edicion = st.tabs([
    "🔍 Consulta",
    "➕ Ingreso",
    "✏️ Editar Stock"
])

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  TAB 1 — CONSULTA / BÚSQUEDA
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_consulta:
    st.subheader("🔍 Buscar Producto")

    if total_productos == 0:
        st.info("📭 El inventario está vacío. Agrega productos en la pestaña **➕ Ingreso**.")
    else:
        # ── Buscador ──────────────────────────────
        busqueda = st.text_input(
            "Escribe el nombre del producto",
            placeholder="ej: labial rojo, tinte negro, base...",
            key="buscador",
            label_visibility="collapsed",
        )

        # ── Filtro por categoría ──────────────────
        cats_disponibles = ["Todas las categorías"] + sorted(df_inventario["Categoría"].unique().tolist())
        cat_filtro = st.selectbox("Filtrar por categoría", cats_disponibles, label_visibility="collapsed")

        # ── Filtro de datos ───────────────────────
        df_vista = df_inventario.copy()

        if busqueda:
            mask = df_vista["Producto"].str.lower().str.contains(busqueda.lower(), na=False)
            df_vista = df_vista[mask]

        if cat_filtro != "Todas las categorías":
            df_vista = df_vista[df_vista["Categoría"] == cat_filtro]

        # ── Mostrar resultados ────────────────────
        st.caption(f"Mostrando {len(df_vista)} de {total_productos} productos")

        if df_vista.empty:
            st.warning("🔎 No se encontraron productos con ese filtro.")
        else:
            # Tabla con formato
            df_display = df_vista.copy()
            df_display["Precio (Bs)"] = df_display["Precio (Bs)"].apply(lambda x: f"Bs {x:,.2f}")
            df_display["Stock"] = df_display["Stock"].astype(str)

            st.dataframe(
                df_display[["Producto", "Categoría", "Stock", "Precio (Bs)"]],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Producto":    st.column_config.TextColumn("📦 Producto", width="large"),
                    "Categoría":   st.column_config.TextColumn("🏷️ Categoría"),
                    "Stock":       st.column_config.TextColumn("📊 Stock"),
                    "Precio (Bs)": st.column_config.TextColumn("💰 Precio"),
                }
            )

        # ── Botón de recarga ──────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Actualizar datos", key="btn_refrescar"):
            st.cache_resource.clear()
            st.rerun()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  TAB 2 — INGRESO DE NUEVO PRODUCTO
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_ingreso:
    st.subheader("➕ Agregar Producto")

    with st.form("form_ingreso", clear_on_submit=True):
        nombre = st.text_input(
            "Nombre del producto *",
            placeholder="ej: Labial Rojo Intenso N°5",
            max_chars=80,
        )

        categoria = st.selectbox("Categoría *", CATEGORIAS)

        col_stock, col_precio = st.columns(2)
        with col_stock:
            stock_nuevo = st.number_input(
                "Stock inicial (unidades) *",
                min_value=0,
                max_value=9999,
                value=1,
                step=1,
            )
        with col_precio:
            precio_nuevo = st.number_input(
                "Precio (Bs) *",
                min_value=0.0,
                max_value=99999.0,
                value=0.0,
                step=0.5,
                format="%.2f",
            )

        submitted = st.form_submit_button("💾 GUARDAR PRODUCTO", use_container_width=True)

    if submitted:
        # Validaciones
        nombre = nombre.strip()
        if not nombre:
            st.markdown('<div class="alerta-err">⚠️ El nombre del producto es obligatorio.</div>', unsafe_allow_html=True)
        elif precio_nuevo <= 0:
            st.markdown('<div class="alerta-err">⚠️ Ingresa un precio mayor a 0.</div>', unsafe_allow_html=True)
        elif nombre.lower() in df_inventario["Producto"].str.lower().tolist():
            st.markdown(f'<div class="alerta-err">⚠️ Ya existe un producto llamado <b>{nombre}</b>. Usa la pestaña de Edición para modificar su stock.</div>', unsafe_allow_html=True)
        else:
            # Crear fila nueva
            nueva_fila = pd.DataFrame([{
                "Producto":              nombre,
                "Categoría":             categoria,
                "Stock":                 int(stock_nuevo),
                "Precio (Bs)":           float(precio_nuevo),
                "Última Actualización":  datetime.now().strftime("%d/%m/%Y %H:%M"),
            }])

            df_actualizado = pd.concat([df_inventario, nueva_fila], ignore_index=True)

            with st.spinner("Guardando en Google Sheets..."):
                ok = guardar_datos(conn, df_actualizado)

            if ok:
                st.markdown(f'<div class="alerta-ok">✅ <b>{nombre}</b> agregado exitosamente con {stock_nuevo} unidades.</div>', unsafe_allow_html=True)
                st.balloons()
                # Recargar datos en la siguiente interacción
                st.cache_resource.clear()
            else:
                st.markdown('<div class="alerta-err">❌ No se pudo guardar. Verifica la conexión con Google Sheets.</div>', unsafe_allow_html=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  TAB 3 — EDICIÓN DE STOCK
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_edicion:
    st.subheader("✏️ Actualizar Stock")

    if total_productos == 0:
        st.info("📭 No hay productos. Agrega uno primero en **➕ Ingreso**.")
    else:
        # ── Selector de producto ──────────────────
        opciones = df_inventario["Producto"].tolist()
        producto_sel = st.selectbox(
            "Selecciona el producto",
            opciones,
            key="sel_producto",
        )

        # Fila seleccionada
        idx = df_inventario[df_inventario["Producto"] == producto_sel].index[0]
        fila = df_inventario.loc[idx]
        stock_actual = int(fila["Stock"])

        # ── Info del producto seleccionado ────────
        st.markdown(f"""
        <div style="background:white;border-radius:14px;padding:1rem 1.2rem;
                    box-shadow:0 2px 10px rgba(0,0,0,0.08);margin-bottom:1rem;">
            <div style="font-size:1.05rem;font-weight:700;color:#2D1B2E;">{producto_sel}</div>
            <div style="color:#6B5672;font-size:0.9rem;margin-top:3px;">{fila['Categoría']}</div>
            <div style="margin-top:0.7rem;display:flex;gap:1rem;align-items:center;">
                <span style="font-size:1.5rem;font-weight:900;color:#E91E8C;">{stock_actual}</span>
                <span style="color:#6B5672;font-size:0.85rem;">unidades en stock</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Botones rápidos +1 / -1 ──────────────
        st.markdown("**Ajuste rápido:**")
        col_menos, col_mas = st.columns(2)

        with col_menos:
            if st.button("➖ Restar 1 unidad", key="btn_menos", disabled=(stock_actual <= 0)):
                nuevo_stock = stock_actual - 1
                df_inventario.at[idx, "Stock"] = nuevo_stock
                df_inventario.at[idx, "Última Actualización"] = datetime.now().strftime("%d/%m/%Y %H:%M")
                with st.spinner("Guardando..."):
                    ok = guardar_datos(conn, df_inventario)
                if ok:
                    st.markdown(f'<div class="alerta-ok">✅ Stock actualizado a <b>{nuevo_stock}</b> unidades.</div>', unsafe_allow_html=True)
                    st.rerun()

        with col_mas:
            if st.button("➕ Sumar 1 unidad", key="btn_mas"):
                nuevo_stock = stock_actual + 1
                df_inventario.at[idx, "Stock"] = nuevo_stock
                df_inventario.at[idx, "Última Actualización"] = datetime.now().strftime("%d/%m/%Y %H:%M")
                with st.spinner("Guardando..."):
                    ok = guardar_datos(conn, df_inventario)
                if ok:
                    st.markdown(f'<div class="alerta-ok">✅ Stock actualizado a <b>{nuevo_stock}</b> unidades.</div>', unsafe_allow_html=True)
                    st.rerun()

        # ── Ajuste manual (cantidad exacta) ──────
        st.markdown("<hr class='separador'>", unsafe_allow_html=True)
        st.markdown("**O ingresa la cantidad exacta:**")

        with st.form("form_stock"):
            col_op, col_cant = st.columns([1, 1])
            with col_op:
                operacion = st.selectbox("Operación", ["➕ Sumar", "➖ Restar", "🔄 Reemplazar"])
            with col_cant:
                cantidad = st.number_input("Cantidad", min_value=1, max_value=9999, value=1, step=1)

            nuevo_precio = st.number_input(
                "Actualizar precio (Bs) — opcional",
                min_value=0.0,
                value=float(fila["Precio (Bs)"]),
                step=0.5,
                format="%.2f",
            )

            guardar = st.form_submit_button("💾 APLICAR CAMBIOS", use_container_width=True)

        if guardar:
            if "Sumar" in operacion:
                nuevo_stock = stock_actual + int(cantidad)
            elif "Restar" in operacion:
                nuevo_stock = max(0, stock_actual - int(cantidad))
            else:  # Reemplazar
                nuevo_stock = int(cantidad)

            df_inventario.at[idx, "Stock"] = nuevo_stock
            df_inventario.at[idx, "Precio (Bs)"] = float(nuevo_precio)
            df_inventario.at[idx, "Última Actualización"] = datetime.now().strftime("%d/%m/%Y %H:%M")

            with st.spinner("Guardando en Google Sheets..."):
                ok = guardar_datos(conn, df_inventario)

            if ok:
                st.markdown(f'<div class="alerta-ok">✅ <b>{producto_sel}</b> actualizado. Nuevo stock: <b>{nuevo_stock}</b> unidades.</div>', unsafe_allow_html=True)
                st.rerun()
            else:
                st.markdown('<div class="alerta-err">❌ Error al guardar. Intenta de nuevo.</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════
#  FOOTER
# ══════════════════════════════════════════════════
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center;color:#B0A0BA;font-size:0.78rem;padding:1rem 0;">
    💄 Zimbawe Beauty · Inventario v1.0<br>
    Desarrollado con Streamlit + Google Sheets
</div>
""", unsafe_allow_html=True)
