import streamlit as st
import requests
import pandas as pd
import os
import re  # Para buscar números en los nombres de los certificados
from dotenv import load_dotenv

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="App BPD", page_icon="🏦", layout="wide")

# Ocultar menú de Streamlit y footer
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

load_dotenv()
CLIENT_ID = os.getenv("BPD_CLIENT_ID")
CLIENT_SECRET = os.getenv("BPD_CLIENT_SECRET")

if not CLIENT_ID or not CLIENT_SECRET:
    st.error("⚠️ Error: No se encontraron las credenciales en el archivo .env")
    st.stop()

# --- 2. CEREBRO DE LA APLICACIÓN (CONFIGURACIÓN DE REGLAS) ---
# Aquí definimos las reglas estrictas de tiempo para cada préstamo
REGLAS_PRESTAMOS = {
    "Personal_Personal": {
        "nombre": "Préstamo Personal",
        "min_meses": 6,
        "max_meses": 60,   # 5 años
        "default": 24
    },
    "LoansPHiRate": {
        "nombre": "Préstamo Hipotecario",
        "min_meses": 12,
        "max_meses": 360,  # 30 años
        "default": 240
    },
    "LoansIndicativePCoRate": {
        "nombre": "Préstamo Vehículo Nuevo",
        "min_meses": 6,
        "max_meses": 84,   # 7 años
        "default": 60
    }
}

# URLs
TOKEN_URL = "https://api.us-east-a.apiconnect.ibmappdomain.cloud/apiportalpopular/bpdsandbox/bpd/Authentication/oauth2/token"
API_URL = "https://api.us-east-a.apiconnect.ibmappdomain.cloud/apiportalpopular/bpdsandbox/consultatasasinteres/consultaTasasInteres"

# --- 3. FUNCIONES DE CONEXIÓN ---


def obtener_token():
    payload = {'grant_type': 'client_credentials', 'scope': 'scope_1',
               'client_id': CLIENT_ID, 'client_secret': CLIENT_SECRET}
    try:
        response = requests.post(TOKEN_URL, data=payload)
        return response.json()['access_token'] if response.status_code == 200 else None
    except:
        return None


def consultar_datos(token):
    headers = {'Authorization': f'Bearer {token}',
               'X-IBM-Client-Id': CLIENT_ID, 'Accept': 'application/json'}
    try:
        response = requests.get(API_URL, headers=headers)
        return response.json() if response.status_code == 200 else None
    except:
        return None

# Función para extraer días del nombre feo del certificado (ej: "OData__x0033_0DaysTermDOP" -> 30)


def extraer_dias_certificado(nombre_tecnico):
    # Buscamos patrones como "30Days", "60Days", etc.
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
    return 30  # Default por si acaso

# --- 4. INTERFAZ PRINCIPAL ---


if 'datos_bancarios' not in st.session_state:
    st.session_state.datos_bancarios = None

with st.sidebar:
    # Truco para centrar la imagen
    col_izq, col_centro, col_der = st.columns([1, 2, 1])
    with col_centro:
        # Asegúrate de que tu imagen sea .png con fondo transparente si es posible
        st.image("assets/image2.png", use_container_width=True)

    st.write("")  # Espacio en blanco para que respire

    # MENÚ NATIVO (Más limpio y rápido)
    opcion_menu = st.radio(
        "Navegación",
        ["Dashboard", "Préstamos", "Inversiones"],
        captions=["Vista general", "Simulador de cuotas",
                  "Simulador de certificados"]
    )

    st.divider()

    if st.button("🔄 Actualizar Tasas", type="primary"):  # Botón nativo
        with st.spinner('Conectando...'):
            token = obtener_token()
            if token:
                data = consultar_datos(token)
                if data:
                    st.session_state.datos_bancarios = data
                    st.toast("Datos actualizados", icon='✅')

# --- LÓGICA DE PANTALLAS ---

if not st.session_state.datos_bancarios:
    st.info(
        "👈 Presiona 'Actualizar Tasas' en el menú lateral para conectar con el banco.")

else:
    data = st.session_state.datos_bancarios
    try:
        tasas_prestamos = data['tasasint'].get('tasaprestamos', {})
        # Lógica para encontrar certificados donde sea que estén
        tasas_certificados = data['tasasint'].get('tasacertificadosObject', {})
        if not tasas_certificados:
            tasas_certificados = data['tasasint'].get('tasacertificados', {})
    except:
        st.stop()

    # ---------------------------------------------------------
    # PANTALLA 1: DASHBOARD
    # ---------------------------------------------------------
    if opcion_menu == "Dashboard":
        st.title("Resumen de Tasas de Mercado")

        st.subheader("🏦 Préstamos Principales")
        c1, c2, c3 = st.columns(3)
        # Solo mostramos los 3 que te interesan
        c1.metric(
            "Personal", f"{tasas_prestamos.get('Personal_Personal', 'N/A')}%")
        c2.metric("Hipotecario",
                  f"{tasas_prestamos.get('LoansPHiRate', 'N/A')}%")
        c3.metric(
            "Vehículo", f"{tasas_prestamos.get('LoansIndicativePCoRate', 'N/A')}%")

        st.subheader("📜 Certificados de Inversión")
        # Mostramos los primeros 3 certificados que encontremos
        keys_cert = list(tasas_certificados.keys())
        cc1, cc2, cc3 = st.columns(3)
        for i, col in enumerate([cc1, cc2, cc3]):
            if i < len(keys_cert):
                nombre_tec = keys_cert[i]
                dias = extraer_dias_certificado(nombre_tec)
                col.metric(f"Certificado {dias} Días",
                           f"{tasas_certificados[nombre_tec]}%")

    # ---------------------------------------------------------
    # PANTALLA 2: PRÉSTAMOS (Lógica estricta)
    # ---------------------------------------------------------
    # ---------------------------------------------------------
    # PANTALLA 2: PRÉSTAMOS (CON GRÁFICOS Y TABLA)
    # ---------------------------------------------------------
    elif opcion_menu == "Préstamos":
        st.title("Simulador de Préstamos")

        col1, col2 = st.columns([1, 2])

        with col1:
            opciones_validas = [
                k for k in tasas_prestamos.keys() if k in REGLAS_PRESTAMOS]

            codigo_seleccionado = st.selectbox(
                "Tipo de Producto",
                opciones_validas,
                format_func=lambda x: REGLAS_PRESTAMOS[x]["nombre"]
            )

            regla_actual = REGLAS_PRESTAMOS[codigo_seleccionado]
            tasa_real = tasas_prestamos[codigo_seleccionado]

            monto = st.number_input(
                "Monto (RD$)", min_value=10000, value=100000, step=10000, format="%d")
            st.caption(f"Visualización: **RD$ {monto:,.2f}**")

        with col2:
            st.subheader("Condiciones")
            plazo = st.slider(
                "Plazo del Préstamo (Meses)",
                min_value=regla_actual["min_meses"],
                max_value=regla_actual["max_meses"],
                value=regla_actual["default"]
            )

            st.info(f"""
            **Producto:** {regla_actual['nombre']} | **Tasa:** {tasa_real}% | **Plazo:** {plazo} meses
            """)

            # --- CÁLCULO DE LA TABLA DE AMORTIZACIÓN ---
            if st.button("Calcular Plan de Pagos", type="primary"):
                i = tasa_real / 100 / 12
                n = plazo

                if i > 0:
                    # 1. Calculamos la cuota fija
                    cuota = (monto * i) / (1 - (1 + i)**(-n))

                    st.success(f"### Cuota Mensual: RD$ {cuota:,.2f}")

                    # 2. Generamos la tabla mes a mes (Ciclo For)
                    saldo = monto
                    datos_amortizacion = []

                    for mes in range(1, n + 1):
                        interes_mes = saldo * i
                        capital_mes = cuota - interes_mes
                        saldo -= capital_mes
                        if saldo < 0:
                            saldo = 0  # Ajuste por decimales

                        datos_amortizacion.append({
                            "Mes": mes,
                            "Cuota": round(cuota, 2),
                            "Interés": round(interes_mes, 2),
                            "Capital": round(capital_mes, 2),
                            "Saldo Restante": round(saldo, 2)
                        })

                    # Convertimos a DataFrame (Tabla inteligente)
                    df_amort = pd.DataFrame(datos_amortizacion)

                    st.divider()

                    # 3. VISUALIZACIÓN GRÁFICA
                    st.subheader("📉 Comportamiento de tu Deuda")
                    # Gráfico simple: Línea de Saldo
                    st.line_chart(df_amort, x="Mes",
                                  y="Saldo Restante", color="#0054a6")

                    # 4. TABLA DETALLADA DESPLEGABLE
                    with st.expander("Ver Tabla de Amortización Completa"):
                        st.dataframe(df_amort, use_container_width=True)

                        # 5. BOTÓN DE DESCARGA (CSV)
                        csv = df_amort.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="📥 Descargar Tabla en Excel (CSV)",
                            data=csv,
                            file_name=f"plan_pagos_{regla_actual['nombre']}.csv",
                            mime='text/csv',
                        )

                else:
                    st.error("Error en tasa")

    # ---------------------------------------------------------
    # PANTALLA 3: INVERSIONES (Plazos Fijos)
    # ---------------------------------------------------------
    elif opcion_menu == "Inversiones":
        st.title("Simulador de Inversiones")

        if not tasas_certificados:
            st.warning("No hay datos de certificados.")
        else:
            col1, col2 = st.columns(2)

            with col1:
                # El usuario elige el certificado
                cert_code = st.selectbox(
                    "Selecciona el Certificado",
                    list(tasas_certificados.keys()),
                    format_func=lambda x: f"Certificado {extraer_dias_certificado(x)} Días"
                )

                tasa_inv = tasas_certificados[cert_code]
                # Detectamos si es 30, 60, 90...
                dias_reales = extraer_dias_certificado(cert_code)

                capital = st.number_input(
                    "Capital a Invertir (RD$)", min_value=10000, value=50000, step=5000, format="%d")
                st.caption(f"Visualización: **RD$ {capital:,.2f}**")

            with col2:
                st.subheader("Detalles del Plazo")
                # LÓGICA DE PLAZO FIJO: El usuario NO puede editar el tiempo
                # Mostramos el tiempo como dato informativo, no como input
                st.metric("Plazo Fijo (Inmodificable)", f"{dias_reales} Días")
                st.metric("Tasa de Retorno", f"{tasa_inv}%")

                if st.button("Calcular Retorno", type="primary"):
                    # Fórmula Interés Simple para días exactos: (Capital * Tasa * Días) / 36000
                    # (36000 es 360 días * 100 del porcentaje)
                    ganancia_bruta = (capital * tasa_inv * dias_reales) / 36000
                    impuesto = ganancia_bruta * 0.10  # 10% de ley
                    ganancia_neta = ganancia_bruta - impuesto

                    st.divider()
                    st.success(f"### Ganancia Neta: RD$ {ganancia_neta:,.2f}")
                    st.text(
                        f"(Ganancia bruta: {ganancia_bruta:,.2f} - Impuesto: {impuesto:,.2f})")
                    st.caption(
                        f"Al finalizar los {dias_reales} días recibirás tu capital + ganancia.")
