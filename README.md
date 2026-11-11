# 🏦 Monitor de Tasas - Banco Popular Dominicano

Aplicación desarrollada en Python y Streamlit que se conecta a la API Sandbox del Banco Popular para visualizar las tasas que devuelve el sandbox y simular cuotas.

## 🚀 Características
- Conexión segura OAuth 2.0 con la API de IBM/BPD.
- **Dashboard:** Visualización de tasas del sandbox.
- **Simulador de Préstamos:** Cálculo de cuotas con amortización y gráficos.
- **Inversiones:** Calculadora de retorno para certificados financieros.

## 🛠️ Tecnologías
- Python 3.10+
- Streamlit
- Pandas
- Requests

## ⚙️ Instalación

Necesitas Git, Python 3.10 o posterior y credenciales OAuth 2.0 de una aplicación con acceso al sandbox del Banco Popular Dominicano.

### 1. Clonar y crear un entorno virtual

```sh
git clone https://github.com/JosuaPerez/monitor-tasas-bpd.git
cd monitor-tasas-bpd
python -m venv .venv
```

En Windows, activa el entorno en PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

En macOS o Linux, usa `python3` para crear el entorno si `python` no está disponible. Luego actívalo:

```sh
source .venv/bin/activate
```

Con el entorno activo, instala las dependencias:

```sh
python -m pip install -r requirements.txt
```

### 2. Configurar el sandbox

Crea un archivo llamado `.env` en la raíz del repositorio, junto a `dashboard_bpd.py`. Sustituye los valores de ejemplo por tus credenciales del sandbox:

```dotenv
BPD_CLIENT_ID=tu_client_id
BPD_CLIENT_SECRET=tu_client_secret
```

Git ignora el archivo `.env`. Mantén tus credenciales en ese archivo local.

### 3. Ejecutar la aplicación

```sh
python -m streamlit run dashboard_bpd.py
```

Abre [http://localhost:8501](http://localhost:8501). Si aparece «Credenciales no encontradas», comprueba que el archivo se llame exactamente `.env` y que ambas variables tengan un valor. La consulta de tasas requiere acceso al sandbox.
