import streamlit as st
import requests
import pandas as pd
import os
import time
from dotenv import load_dotenv
import streamlit.components.v1 as components

# --- 1. CONFIGURACIÓN INICIAL ---
st.set_page_config(
    page_title="App BPD",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed"  # Arranca cerrado
)

# --- CSS: BOTONES GRANDES Y AJUSTES MÓVIL ---
st.markdown("""
    <style>
        /* Aumentar tamaño de opciones del menú para dedos */
        .stRadio label {
            font-size: 1.2rem !important;
            padding: 15px !important; /* Más área de contacto */
            cursor: pointer;
        }
        
        /* Ajustes visuales para móvil */
        @media (max-width: 600px) {
            .block-container {
                padding-top: 1rem !important;
                padding-left: 0.5rem !important;
                padding-right: 0.5rem !important;
            }
            h1 { font-size: 1.8rem !important; }
            h2, h3 { font-size: 1.4rem !important; }
            
            /* Tarjetas métricas */
            [data-testid="stMetric"] {
                background-color: rgba(255, 255, 255, 0.05); 
                border: 1px solid rgba(255, 255, 255, 0.1);
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 10px;
            }
        }
        
        /* Limpieza de interfaz */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        div.stButton > button:first-child {
            border-radius: 8px;
            font-weight: bold;
            height: 3em; 
        }
    </style>
""", unsafe_allow_html=True)

# --- 2. CARGA DE CREDENCIALES ---
load_dotenv()
CLIENT_ID = os.getenv("BPD_CLIENT_ID")
CLIENT_SECRET = os.getenv("BPD_CLIENT_SECRET")

if not CLIENT_ID or not CLIENT_SECRET:
    st.error("⚠️ Error: Credenciales no encontradas.")
    st.stop()

# --- 3. REGLAS DE NEGOCIO ---
REGLAS_PRESTAMOS = {
    "Personal_Personal": {"nombre": "Préstamo Personal", "min_meses": 6, "max_meses": 60, "default": 24},
    "LoansPHiRate": {"nombre": "Préstamo Hipotecario", "min_meses": 12, "max_meses": 360, "default": 240},
    "LoansIndicativePCoRate": {"nombre": "Préstamo Vehículo Nuevo", "min_meses": 6, "max_meses": 84, "default": 60}
}

# URLs
TOKEN_URL = "https://api.us-east-a.apiconnect.ibmappdomain.cloud/apiportalpopular/bpdsandbox/bpd/Authentication/oauth2/token"
API_URL = "https://api.us-east-a.apiconnect.ibmappdomain.cloud/apiportalpopular/bpdsandbox/consultatasasinteres/consultaTasasInteres"

# --- 4. FUNCIONES ---

def obtener_token():
    try:
        payload = {'grant_type': 'client_credentials', 'scope': 'scope_1',
                   'client_id': CLIENT_ID, 'client_secret': CLIENT_SECRET}
        response = requests.post(TOKEN_URL, data=payload)
        return response.json()['access_token'] if response.status_code == 200 else None
    except:
        return None

def consultar_datos(token):
    try:
        headers = {'Authorization': f'Bearer {token}',
                   'X-IBM-Client-Id': CLIENT_ID, 'Accept': 'application/json'}
        response = requests.get(API_URL, headers=headers)
        return response.json() if response.status_code == 200 else None
    except:
        return None

def extraer_dias_certificado(nombre_tecnico):
    if "30Days" in nombre_tecnico or "x0033_0Days" in nombre_tecnico:
        return 30
    if "60Days" in nombre_tecnico or "x0036_0Days" in nombre_tecnico:
        return 60
    if "90Days" in nombre_tecnico or "x0039_0Days" in nombre_tecnico:
        return 90
    if "180Days" in nombre_tecnico or "x0031_80Days" in nombre_tecnico:
        return 180
    if "360Days" in nombre_tecnico or "x0033_60Days" in nombre_tecnico:
        return 360
    return 30

# --- CALLBACK IMPORTANTE ---
# Esta función activa la señal para que el JS se ejecute

def cerrar_sidebar():
    st.session_state.cerrar_menu_ahora = True

if 'datos_bancarios' not in st.session_state:
    st.session_state.datos_bancarios = None
if 'cerrar_menu_ahora' not in st.session_state:
    st.session_state.cerrar_menu_ahora = False

# --- 5. INTERFAZ: BARRA LATERAL ---
with st.sidebar:
    st.image("assets/image2.png", use_container_width=True)
    st.write("")
    st.write("")

    opcion_menu = st.radio(
        "Navegación",
        ["Dashboard", "Préstamos", "Inversiones"],
        key="navegacion_radio",
        on_change=cerrar_sidebar 
    )

# --- LÓGICA JAVASCRIPT: SOLO MÓVIL ---
if st.session_state.cerrar_menu_ahora:
    ts = time.time()
    components.html(f"""
        <script>
            // Timestamp: {ts}
            function closeSidebarMobile() {{
                // 1. Detectar si es móvil (ancho menor a 800px)
                if (window.innerWidth <= 800) {{
                    
                    const parentDoc = window.parent.document;
                    const sidebar = parentDoc.querySelector('[data-testid="stSidebar"]');
                    
                    if (sidebar) {{
                        // Verificar si está visible
                        const style = window.parent.getComputedStyle(sidebar);
                        if (style.width !== '0px' && style.visibility !== 'hidden') {{
                            
                            // Intentar encontrar el botón de colapsar (X)
                            // En móviles suele ser un botón dentro del sidebar con un SVG
                            const buttons = sidebar.querySelectorAll('button');
                            
                            // Estrategia: Clicar el primer botón que encontremos (la X suele ser el primero)
                            if (buttons.length > 0) {{
                                buttons[0].click();
                            }}
                            
                            // Estrategia de respaldo: Buscar por atributo específico
                            const collapseBtn = parentDoc.querySelector('[data-testid="stSidebarCollapseButton"]');
                            if (collapseBtn) {{
                                collapseBtn.click();
                            }}
                        }}
                    }}
                }}
            }}

            closeSidebarMobile();
        </script>
    """, height=0, width=0)

    st.session_state.cerrar_menu_ahora = False

# --- 6. PANTALLAS PRINCIPALES ---
if not st.session_state.datos_bancarios:
    col_izq, col_centro, col_der = st.columns([1, 6, 1])
    with col_centro:
        st.write("")
        st.write("")
        st.markdown("### 👋 ¡Bienvenido al Monitor BPD!")
        st.markdown("""
        Esta aplicación se conecta al **Sandbox del Banco Popular** para traerte:
        * 📉 Tasas de préstamos actualizadas.
        * 💰 Simulador de cuotas.
        * 📈 Calculadora de inversiones.
        """)
        st.write("")
        if st.button("🚀 Conectar y Ver Tasas", type="primary", use_container_width=True):
            with st.spinner('Conectando...'):
                token = obtener_token()
                if token:
                    data = consultar_datos(token)
                    if data:
                        st.session_state.datos_bancarios = data
                        st.toast("¡Conexión exitosa!", icon='🎉')
                        st.rerun()
else:
    data = st.session_state.datos_bancarios
    try:
        tasas_prestamos = data['tasasint'].get('tasaprestamos', {})
        tasas_certificados = data['tasasint'].get('tasacertificadosObject', {})
        if not tasas_certificados:
            tasas_certificados = data['tasasint'].get('tasacertificados', {})
    except Exception as e:
        st.error(f"Error procesando datos: {e}")
        st.stop()

    if opcion_menu == "Dashboard":
        st.title("Resumen de Tasas de Mercado")
        st.subheader("🏦 Préstamos Principales")
        c1, c2, c3 = st.columns(3)
        c1.metric(
            "Personal", f"{tasas_prestamos.get('Personal_Personal', 'N/A')}%")
        c2.metric("Hipotecario",
                  f"{tasas_prestamos.get('LoansPHiRate', 'N/A')}%")
        c3.metric(
            "Vehículo", f"{tasas_prestamos.get('LoansIndicativePCoRate', 'N/A')}%")

        st.subheader("📜 Certificados de Inversión")
        keys_cert = list(tasas_certificados.keys())
        cc1, cc2, cc3 = st.columns(3)
        for i, col in enumerate([cc1, cc2, cc3]):
            if i < len(keys_cert):
                nombre_tec = keys_cert[i]
                dias = extraer_dias_certificado(nombre_tec)
                col.metric(f"Certificado {dias} Días",
                           f"{tasas_certificados[nombre_tec]}%")

    elif opcion_menu == "Préstamos":
        st.title("Simulador de Préstamos")
        col1, col2 = st.columns([1, 2])
        with col1:
            opciones_validas = [
                k for k in tasas_prestamos.keys() if k in REGLAS_PRESTAMOS]
            codigo_seleccionado = st.selectbox(
                "Tipo de Producto", opciones_validas, format_func=lambda x: REGLAS_PRESTAMOS[x]["nombre"])
            regla_actual = REGLAS_PRESTAMOS[codigo_seleccionado]
            tasa_real = tasas_prestamos[codigo_seleccionado]
            monto = st.number_input(
                "Monto (RD$)", min_value=10000, value=100000, step=10000, format="%d")
            st.caption(f"Visualización: **RD$ {monto:,.2f}**")

        with col2:
            st.subheader("Condiciones")
            plazo = st.slider(
                "Plazo (Meses)", min_value=regla_actual["min_meses"], max_value=regla_actual["max_meses"], value=regla_actual["default"])
            st.info(
                f"**Producto:** {regla_actual['nombre']} | **Tasa:** {tasa_real}% | **Plazo:** {plazo} meses")

            if st.button("Calcular Plan de Pagos", type="primary", use_container_width=True):
                i = tasa_real / 100 / 12
                n = plazo
                if i > 0:
                    cuota = (monto * i) / (1 - (1 + i)**(-n))
                    st.success(f"### Cuota Mensual: RD$ {cuota:,.2f}")
                    saldo = monto
                    datos_amortizacion = []
                    for mes in range(1, n + 1):
                        interes_mes = saldo * i
                        capital_mes = cuota - interes_mes
                        saldo -= capital_mes
                        if saldo < 0:
                            saldo = 0
                        datos_amortizacion.append({"Mes": mes, "Cuota": round(cuota, 2), "Interés": round(
                            interes_mes, 2), "Capital": round(capital_mes, 2), "Saldo Restante": round(saldo, 2)})
                    df_amort = pd.DataFrame(datos_amortizacion)
                    st.divider()
                    st.subheader("📉 Comportamiento de tu Deuda")
                    st.line_chart(df_amort, x="Mes", y="Saldo Restante",
                                  color="#0054a6", use_container_width=True)
                    with st.expander("Ver Tabla de Amortización Completa"):
                        st.dataframe(df_amort, use_container_width=True)
                        csv = df_amort.to_csv(index=False).encode('utf-8')
                        st.download_button(label="📥 Descargar Tabla (CSV)", data=csv,
                                           file_name=f"plan_pagos_{regla_actual['nombre']}.csv", mime='text/csv', use_container_width=True)
                else:
                    st.error("Error en tasa")

    elif opcion_menu == "Inversiones":
        st.title("Simulador de Inversiones")
        if not tasas_certificados:
            st.warning("No hay datos de certificados.")
        else:
            col1, col2 = st.columns(2)
            with col1:
                cert_code = st.selectbox("Selecciona el Certificado", list(tasas_certificados.keys(
                )), format_func=lambda x: f"Certificado {extraer_dias_certificado(x)} Días")
                tasa_inv = tasas_certificados[cert_code]
                dias_reales = extraer_dias_certificado(cert_code)
                capital = st.number_input(
                    "Capital a Invertir (RD$)", min_value=10000, value=50000, step=5000, format="%d")
                st.caption(f"Visualización: **RD$ {capital:,.2f}**")
            with col2:
                st.subheader("Detalles del Plazo")
                st.metric("Plazo Fijo", f"{dias_reales} Días")
                st.metric("Tasa de Retorno", f"{tasa_inv}%")
                if st.button("Calcular Retorno", type="primary", use_container_width=True):
                    ganancia_bruta = (capital * tasa_inv * dias_reales) / 36000
                    impuesto = ganancia_bruta * 0.10
                    ganancia_neta = ganancia_bruta - impuesto
                    st.divider()
                    st.success(f"### Ganancia Neta: RD$ {ganancia_neta:,.2f}")
                    st.text(
                        f"(Ganancia bruta: {ganancia_bruta:,.2f} - Impuesto: {impuesto:,.2f})")
                    st.caption(
                        f"Al finalizar los {dias_reales} días recibirás tu capital + ganancia.")
