# SIU 2 - Sistema de Gestión Académica (Backend API)

API REST para el sistema **SIU 2**, desarrollada en Python utilizando el framework **Flask** y **MySQL** como motor de base de datos a través de consultas SQL nativas (sin uso de ORM). El sistema cuenta con autenticación basada en JWT, control de acceso por roles y configuraciones desacopladas mediante variables de entorno.

---

## 📋 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado lo siguiente en tu equipo:
* **Python 3.10 o superior** (Asegúrate de marcar la opción "Add Python to PATH" durante la instalación en Windows).
* **MySQL Server** (A través de XAMPP, Laragon, MySQL Installer o Docker).
* **Git** (Para clonar y gestionar el repositorio).

---

## 🛠️ Instalación y Configuración

Sigue estos pasos en orden para levantar el entorno de desarrollo local.

### 1. Clonar el Repositorio
Abre tu terminal y clona el proyecto:
```bash
git clone <URL_DEL_REPOSITORIO>
cd <NOMBRE_DE_LA_CARPETA_DEL_PROYECTO>
```

### 2. Creación y Activación del Entorno Virtual (Virtualenv)

El entorno virtual aísla las librerías del proyecto para que no generen conflictos con otras aplicaciones de tu sistema.

#### 🪟 En Windows:
* **Crear el entorno virtual:**
  ```bash
  python -m venv venv
  ```
* **Activar el entorno virtual:**
  * Si usas **Símbolo del Sistema (CMD)**:
    ```cmd
    venv\Scripts\activate.bat
    ```
  * Si usas **PowerShell** (Si te arroja un error de restricciones, ejecuta primero `Set-ExecutionPolicy RemoteSigned -Scope Process`):
    ```powershell
    venv\Scripts\activate.ps1
    ```

#### 🐧 🍏 En Linux / macOS:
* **Crear el entorno virtual:**
  ```bash
  python3 -m venv venv
  ```
* **Activar el entorno virtual:**
  ```bash
  source venv/bin/activate
  ```

*(Sabrás que está activo porque verás el texto `(venv)` al principio de la línea de comandos de tu terminal).*

### 3. Instalar las Dependencias
Con el entorno virtual activo, ejecuta el siguiente comando para instalar todas las librerías necesarias:
```bash
pip install -r requirements.txt
```
*Nota: Las librerías principales que se instalarán son `Flask`, `Flask-JWT-Extended`, `mysql-connector-python` y `python-dotenv`.*

### 4. Configurar las Variables de Entorno (`.env`)
El proyecto utiliza un archivo `.env` para almacenar credenciales y configuraciones locales que **no deben subirse a GitHub** bajo ninguna circunstancia.

1. En la raíz del proyecto, busca el archivo plantilla llamado `.env.example`.
2. Duplica el archivo y cámbiale el nombre a `.env`.
3. Abre el archivo `.env` y edita los valores según la configuración de tu computadora local:

```env
# ====== SEGURIDAD (JWT) ======
# Frase secreta para firmar los tokens. Cambiar por una cadena larga en producción.
JWT_SECRET_KEY=coloca_aqui_una_frase_secreta_y_larga_para_firmar_tokens
JWT_ACCESS_TOKEN_EXPIRES_HOURS=2

# ====== BASE DE DATOS (MYSQL) ======
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=tu_contraseña_de_mysql 
DB_NAME=siu2_db
DB_PORT=3306                         # Puerto estándar de MySQL

# ====== REGLAS DE NEGOCIO ======
DOMINIOS_EMAIL_PERMITIDOS=gmail.com,fi.uba.ar

# ====== FRONTEND ======
FRONTEND_URL= # Por ahora no hay
```

### 5. Inicialización de la Base de Datos
Asegúrate de tener tu servidor de MySQL encendido (ej. el módulo MySQL activo en el panel de XAMPP) antes de proceder. El archivo de conexión cuenta con la lógica para crear la base de datos de forma automática si aún no existe en tu servidor local.

Si es la primera vez que lo ejecutas hace lo siguiente para crear la base de datos de SIU 2:
```bash
python init_db.py
```

---

## 🚀 Ejecución del Servidor

Una vez completados los pasos anteriores, puedes iniciar el backend de Flask ejecutando:

```bash
flask run
```
O de forma alternativa:
```bash
python app.py
```

El servidor web se levantará localmente y estará escuchando peticiones en:
👉 `http://localhost:5000/`
