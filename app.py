"""
╔══════════════════════════════════════════════════════════╗
║         ZIMBAWE BEAUTY - SISTEMA DE INVENTARIO           ║
║         Stack: Streamlit + Google Sheets                  ║
║         Mobile-First | Gratis | Sin servidor propio       ║
╚══════════════════════════════════════════════════════════╝

Hoja de Google Sheets requerida:
  - Nombre de la hoja (pestaña): InventarioZimbawe
  - Encabezados fila 1 (exactos, sin espacios extra):
      id | nombre | categoria | cantidad | precio | fecha_actualizacion

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
:root {
    --rosa:       #E91E8C;
    --rosa-claro: #F8BBD9;
    --dorado:     #C8973A;
    --fondo:      #FFF9FC;
    --texto:      #2D1B2E;
    --gris:       #6B5672;
    --radio:      14px;
}
.stApp { background: var(--fondo); }
.block-container { padding: 1rem 1rem 4rem; max-width: 700px; }

.brand-header {
    background: linear-gradient(135deg, #E91E8C 0%, #9C27B0 100%);
    border-radius: var(--radio); padding: 1.2rem 1.5rem;
    text-align: center; margin-bottom: 1.2rem;
    box-shadow: 0 4px 20px rgba(233,30,140,0.3);
}
.brand-header h1 { color:white; font-size:1.8rem; margin:0; letter-spacing:1px; }
.brand-header p  { color:rgba(255,255,255,0.85); margin:0.2rem 0 0; font-size:0.9rem; }

.stTabs [data-baseweb="tab-list"] {
    gap:6px; background:white; border-radius:var(--radio);
    padding:6px; box-shadow:0 2px 8px rgba(0,0,0,0.08);
}
.stTabs [data-baseweb="tab"] {
    border-radius:10px !important; padding:0.6rem 1rem !important;
    font-weight:600 !important; font-size:0.95rem !important; color:var(--gris) !important;
}
.stTabs [aria-selected="true"] {
    background:linear-gradient(135deg,#E91E8C,#9C27B0) !important; color:white !important;
}

.stButton > button {
    width:100%; min-height:3rem; font-size:1rem; font-weight:700;
    border-radius:var(--radio); border:none;
    background:linear-gradient(135deg,#E91E8C,#9C27B0);
    color:white; transition:all 0.2s; box-shadow:0 3px 12px rgba(233,30,140,0.35);
}
.stButton > button:hover { transform:translateY(-1px); box-shadow:0 5px 18px rgba(233,30,140,0.45); }

.stTextInput input, .stNumberInput input {
    font-size:1.05rem !important; padding:0.6rem 0.8rem !important;
    border-radius:10px !important; border:2px solid #EDD9F0 !important;
}

.metric-card {
    background:white; border-radius:var(--radio); padding:1rem;
    text-align:center; box-shadow:0 2px 10px rgba(0,0,0,0.07);
    border-left:4px solid var(--rosa);
}
.metric-card .num   { font-size:2rem; font-weight:800; color:var(--rosa); }
.metric-card .label { font-size:0.8rem; color:var(--gris); font-weight:600; text-transform:uppercase; }

.alerta-ok  { background:#d1f2eb; color:#0a6b4c; border-radius:10px; padding:0.8rem 1rem; margin:0.5rem 0; font-weight:600; }
.alerta-err { background:#f8d7da; color:#721c24; border-radius:10px; padding:0.8rem 1rem; margin:0.5rem 0; font-weight:600; }
.stDataFrame { border-radius:var(--radio); overflow:hidden; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════
#  CONSTANTES — nombres EXACTOS de tu Google Sheet
# ══════════════════════════════════════════════════
WORKSHEET    = "InventarioZimbawe"   # ← nombre de la pestaña

COL_ID       = "id"
COL_NOMBRE   = "nombre"
COL_CAT      = "categoria"
COL_CANTIDAD = "cantidad"
COL_PRECIO   = "precio"
COL_FECHA    = "fecha_actualizacion"

COLUMNAS_SHEET = [COL_ID, COL_NOMBRE, COL_CAT, COL_CANTIDAD, COL_PRECIO, COL_FECHA]

CATEGORIAS = [
    "💋 Labial", "🌸 Base/Corrector", "💅 Esmalte",
    "👁️ Sombra/Delineador", "🧴 Tinte/Coloración",
    "✨ Cuidado Facial", "🛁 Cuidado Corporal", "🌿 Cabello",
    "💎 Perfumería", "🎨 Maquillaje Varios",
]
STOCK_ALERTA = 5

# ══════════════════════════════════════════════════
#  CONEXIÓN A GOOGLE SHEETS
# ══════════════════════════════════════════════════
@st.cache_resource(ttl=30)
def get_connection():
    return st.connection("gsheets", type=GSheetsConnection)


def cargar_datos(conn) -> pd.DataFrame:
    """Lee la hoja InventarioZimbawe y devuelve DataFrame limpio."""
    try:
        df = conn.read(
            worksheet=WORKSHEET,
            usecols=list(range(len(COLUMNAS_SHEET))),
            ttl=10,
        )
        df = df.dropna(subset=[COL_NOMBRE])
        df = df[df[COL_NOMBRE].astype(str).str.strip() != ""]
        df[COL_ID]       = df[COL_ID].fillna("").astype(str)
        df[COL_CANTIDAD] = pd.to_numeric(df[COL_CANTIDAD], errors="coerce").fillna(0).astype(int)
        df[COL_PRECIO]   = pd.to_numeric(df[COL_PRECIO],   errors="coerce").fillna(0.0)
        return df.reset_index(drop=True)
    except Exception as e:
        st.error(f"⚠️ Error al leer Google Sheets: {e}")
        return pd.DataFrame(columns=COLUMNAS_SHEET)


def guardar_datos(conn, df: pd.DataFrame) -> bool:
    """Escribe el DataFrame completo a la hoja."""
    try:
        conn.update(worksheet=WORKSHEET, data=df)
        st.cache_resource.clear()
        return True
    except Exception as e:
        st.error(f"⚠️ Error al guardar: {e}")
        return False


def generar_id(df: pd.DataFrame) -> str:
    """Genera ID correlativo: ZB-001, ZB-002, ..."""
    nums = []
    for v in df[COL_ID].tolist():
        try:
            nums.append(int(str(v).replace("ZB-", "")))
        except Exception:
            pass
    return f"ZB-{max(nums, default=0) + 1:03d}"


# ══════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════
st.markdown("""
<div class="brand-header">
    <h1>💄 Zimbawe Beauty</h1>
    <p>Sistema de Inventario · Rápido · Desde cualquier lugar</p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════
#  CARGA INICIAL
# ══════════════════════════════════════════════════
conn = get_connection()
df_inventario = cargar_datos(conn)

total_productos = len(df_inventario)
sin_stock  = int((df_inventario[COL_CANTIDAD] == 0).sum())               if total_productos > 0 else 0
stock_bajo = int(((df_inventario[COL_CANTIDAD] > 0) &
                  (df_inventario[COL_CANTIDAD] <= STOCK_ALERTA)).sum())  if total_productos > 0 else 0

# ── Métricas ──────────────────────────────────────
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f'<div class="metric-card"><div class="num">{total_productos}</div><div class="label">Productos</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-card" style="border-color:#E67E22;"><div class="num" style="color:#E67E22;">{stock_bajo}</div><div class="label">Stock Bajo</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-card" style="border-color:#E74C3C;"><div class="num" style="color:#E74C3C;">{sin_stock}</div><div class="label">Sin Stock</div></div>', unsafe_allow_html=True)

st.markdown("<hr style='border:none;border-top:2px dashed #EDD9F0;margin:1.2rem 0;'>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════
#  TABS
# ══════════════════════════════════════════════════
tab_consulta, tab_ingreso, tab_edicion = st.tabs(["🔍 Consulta", "➕ Ingreso", "✏️ Editar Stock"])

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  TAB 1 — CONSULTA
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_consulta:
    st.subheader("🔍 Buscar Producto")

    if total_productos == 0:
        st.info("📭 El inventario está vacío. Agrega productos en **➕ Ingreso**.")
    else:
        busqueda = st.text_input(
            "Buscar", placeholder="ej: labial, tinte, base...",
            key="buscador", label_visibility="collapsed",
        )
        cats = ["Todas las categorías"] + sorted(df_inventario[COL_CAT].unique().tolist())
        cat_filtro = st.selectbox("Categoría", cats, label_visibility="collapsed")

        df_vista = df_inventario.copy()
        if busqueda:
            df_vista = df_vista[df_vista[COL_NOMBRE].str.lower().str.contains(busqueda.lower(), na=False)]
        if cat_filtro != "Todas las categorías":
            df_vista = df_vista[df_vista[COL_CAT] == cat_filtro]

        st.caption(f"Mostrando {len(df_vista)} de {total_productos} productos")

        if df_vista.empty:
            st.warning("🔎 No se encontraron productos.")
        else:
            df_show = df_vista.copy()
            df_show[COL_PRECIO]   = df_show[COL_PRECIO].apply(lambda x: f"Bs {x:,.2f}")
            df_show[COL_CANTIDAD] = df_show[COL_CANTIDAD].astype(str)
            st.dataframe(
                df_show[[COL_ID, COL_NOMBRE, COL_CAT, COL_CANTIDAD, COL_PRECIO]],
                use_container_width=True,
                hide_index=True,
                column_config={
                    COL_ID:       st.column_config.TextColumn("🔖 id"),
                    COL_NOMBRE:   st.column_config.TextColumn("📦 nombre", width="large"),
                    COL_CAT:      st.column_config.TextColumn("🏷️ categoria"),
                    COL_CANTIDAD: st.column_config.TextColumn("📊 cantidad"),
                    COL_PRECIO:   st.column_config.TextColumn("💰 precio"),
                },
            )

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Actualizar datos", key="btn_ref"):
            st.cache_resource.clear()
            st.rerun()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  TAB 2 — INGRESO
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_ingreso:
    st.subheader("➕ Agregar Producto")

    with st.form("form_ingreso", clear_on_submit=True):
        nombre_inp = st.text_input("Nombre del producto *", placeholder="ej: Labial Rojo Intenso N°5", max_chars=80)
        cat_inp    = st.selectbox("Categoría *", CATEGORIAS)

        cc, cp = st.columns(2)
        with cc:
            cant_inp = st.number_input("Cantidad inicial *", min_value=0, max_value=9999, value=1, step=1)
        with cp:
            precio_inp = st.number_input("Precio (Bs) *", min_value=0.0, max_value=99999.0, value=0.0, step=0.5, format="%.2f")

        submitted = st.form_submit_button("💾 GUARDAR PRODUCTO", use_container_width=True)

    if submitted:
        nombre_clean = nombre_inp.strip()
        if not nombre_clean:
            st.markdown('<div class="alerta-err">⚠️ El nombre es obligatorio.</div>', unsafe_allow_html=True)
        elif precio_inp <= 0:
            st.markdown('<div class="alerta-err">⚠️ El precio debe ser mayor a 0.</div>', unsafe_allow_html=True)
        elif nombre_clean.lower() in df_inventario[COL_NOMBRE].str.lower().tolist():
            st.markdown(f'<div class="alerta-err">⚠️ Ya existe "<b>{nombre_clean}</b>". Edita su stock en ✏️ Editar Stock.</div>', unsafe_allow_html=True)
        else:
            nid = generar_id(df_inventario)
            nueva = pd.DataFrame([{
                COL_ID:       nid,
                COL_NOMBRE:   nombre_clean,
                COL_CAT:      cat_inp,
                COL_CANTIDAD: int(cant_inp),
                COL_PRECIO:   float(precio_inp),
                COL_FECHA:    datetime.now().strftime("%d/%m/%Y %H:%M"),
            }])
            df_upd = pd.concat([df_inventario, nueva], ignore_index=True)
            with st.spinner("Guardando en Google Sheets..."):
                ok = guardar_datos(conn, df_upd)
            if ok:
                st.markdown(f'<div class="alerta-ok">✅ <b>{nombre_clean}</b> guardado con ID <b>{nid}</b> y {int(cant_inp)} unidades.</div>', unsafe_allow_html=True)
                st.balloons()
                st.cache_resource.clear()
            else:
                st.markdown('<div class="alerta-err">❌ No se pudo guardar. Verifica la conexión.</div>', unsafe_allow_html=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  TAB 3 — EDICIÓN DE STOCK
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_edicion:
    st.subheader("✏️ Actualizar Stock")

    if total_productos == 0:
        st.info("📭 No hay productos. Agrega uno primero en **➕ Ingreso**.")
    else:
        opciones = df_inventario.apply(lambda r: f"{r[COL_ID]} — {r[COL_NOMBRE]}", axis=1).tolist()
        sel      = st.selectbox("Selecciona el producto", opciones, key="sel_prod")
        idx      = opciones.index(sel)
        fila     = df_inventario.loc[idx]
        stock_actual = int(fila[COL_CANTIDAD])

        # Tarjeta info
        st.markdown(f"""
        <div style="background:white;border-radius:14px;padding:1rem 1.2rem;
                    box-shadow:0 2px 10px rgba(0,0,0,0.08);margin-bottom:1rem;">
            <div style="font-size:0.78rem;color:#B0A0BA;font-weight:600;">{fila[COL_ID]}</div>
            <div style="font-size:1.05rem;font-weight:700;color:#2D1B2E;margin-top:2px;">{fila[COL_NOMBRE]}</div>
            <div style="color:#6B5672;font-size:0.9rem;margin-top:3px;">{fila[COL_CAT]}</div>
            <div style="margin-top:0.8rem;display:flex;gap:1rem;align-items:center;">
                <span style="font-size:1.5rem;font-weight:900;color:#E91E8C;">{stock_actual}</span>
                <span style="color:#6B5672;font-size:0.85rem;">unidades · </span>
                <span style="font-weight:700;color:#C8973A;">Bs {float(fila[COL_PRECIO]):,.2f}</span>
            </div>
        </div>""", unsafe_allow_html=True)

        # Botones rápidos
        st.markdown("**Ajuste rápido:**")
        cm, cp2 = st.columns(2)

        with cm:
            if st.button("➖ Restar 1", key="btn_menos", disabled=(stock_actual <= 0)):
                ns = stock_actual - 1
                df_inventario.at[idx, COL_CANTIDAD] = ns
                df_inventario.at[idx, COL_FECHA]    = datetime.now().strftime("%d/%m/%Y %H:%M")
                with st.spinner("Guardando..."):
                    ok = guardar_datos(conn, df_inventario)
                if ok:
                    st.markdown(f'<div class="alerta-ok">✅ Nuevo stock: <b>{ns}</b> unidades.</div>', unsafe_allow_html=True)
                    st.rerun()

        with cp2:
            if st.button("➕ Sumar 1", key="btn_mas"):
                ns = stock_actual + 1
                df_inventario.at[idx, COL_CANTIDAD] = ns
                df_inventario.at[idx, COL_FECHA]    = datetime.now().strftime("%d/%m/%Y %H:%M")
                with st.spinner("Guardando..."):
                    ok = guardar_datos(conn, df_inventario)
                if ok:
                    st.markdown(f'<div class="alerta-ok">✅ Nuevo stock: <b>{ns}</b> unidades.</div>', unsafe_allow_html=True)
                    st.rerun()

        # Ajuste exacto
        st.markdown("<hr style='border:none;border-top:2px dashed #EDD9F0;margin:1.2rem 0;'>", unsafe_allow_html=True)
        st.markdown("**O ajusta una cantidad específica:**")

        with st.form("form_stock"):
            co, ca = st.columns(2)
            with co:
                operacion = st.selectbox("Operación", ["➕ Sumar", "➖ Restar", "🔄 Reemplazar"])
            with ca:
                cantidad = st.number_input("Cantidad", min_value=1, max_value=9999, value=1, step=1)

            nuevo_precio_f = st.number_input(
                "Actualizar precio (Bs) — opcional",
                min_value=0.0, value=float(fila[COL_PRECIO]), step=0.5, format="%.2f",
            )
            guardar = st.form_submit_button("💾 APLICAR CAMBIOS", use_container_width=True)

        if guardar:
            if "Sumar"      in operacion: ns = stock_actual + int(cantidad)
            elif "Restar"   in operacion: ns = max(0, stock_actual - int(cantidad))
            else:                          ns = int(cantidad)

            df_inventario.at[idx, COL_CANTIDAD] = ns
            df_inventario.at[idx, COL_PRECIO]   = float(nuevo_precio_f)
            df_inventario.at[idx, COL_FECHA]    = datetime.now().strftime("%d/%m/%Y %H:%M")

            with st.spinner("Guardando en Google Sheets..."):
                ok = guardar_datos(conn, df_inventario)
            if ok:
                st.markdown(f'<div class="alerta-ok">✅ <b>{fila[COL_NOMBRE]}</b> actualizado. Nuevo stock: <b>{ns}</b>.</div>', unsafe_allow_html=True)
                st.rerun()
            else:
                st.markdown('<div class="alerta-err">❌ Error al guardar. Intenta de nuevo.</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════
#  FOOTER
# ══════════════════════════════════════════════════
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center;color:#B0A0BA;font-size:0.78rem;padding:1rem 0;">
    💄 Zimbawe Beauty · Inventario v1.1<br>
    Hoja: <code>InventarioZimbawe</code> · Columnas: <code>id · nombre · categoria · cantidad · precio · fecha_actualizacion</code>
</div>
""", unsafe_allow_html=True)
