import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import mysql.connector
import bcrypt
import os
import subprocess

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DE LA CONEXIÓN A LA BASE DE DATOS
# -----------------------------------------------------------------------------
db_config = {
    'user': 'root',
    'password': 'usuario',
    'host': 'localhost',
    'database': 'weady'  # Asegúrate de que este nombre sea el correcto
}

# -----------------------------------------------------------------------------
# DEFINICIÓN DE COLORES
# -----------------------------------------------------------------------------
BG_APP = "#FB8C00"       # Color de fondo general de la aplicación
BG_PANEL = "#FFCC80"     # Color para paneles y botones

# -----------------------------------------------------------------------------
# FUNCIÓN: load_logo()
# Objetivo: Cargar y redimensionar el logo de la aplicación.
# -----------------------------------------------------------------------------
def load_logo():
    try:
        image = Image.open("imagenes/logo.png")  # Cargar el logo desde la carpeta "imagenes"
        image = image.resize((150, 150))           # Redimensionar la imagen a 150x150 píxeles
        return ImageTk.PhotoImage(image)           # Convertir la imagen para usarla en Tkinter
    except Exception as e:
        print(f"Error al cargar el logo: {e}")
        return None

# -----------------------------------------------------------------------------
# FUNCIÓN: open_register_window()
# Objetivo: Abrir una ventana secundaria para que el usuario se registre.
# Se definen variables globales para que los widgets sean accesibles desde register().
# -----------------------------------------------------------------------------
def open_register_window():
    global register_window, reg_entry_name, reg_entry_email, reg_entry_password, reg_entry_city
    register_window = tk.Toplevel(app)  # Crear una ventana secundaria (Toplevel)
    register_window.title("Registro")     # Establecer el título de la ventana
    register_window.configure(bg=BG_APP)  # Establecer el color de fondo

    # Cargar y mostrar el logo en la ventana de registro
    logo = load_logo()
    if logo:
        logo_label = tk.Label(register_window, image=logo, bg=BG_APP)
        logo_label.image = logo  # Guardar referencia para evitar que se elimine la imagen
        logo_label.grid(row=0, column=0, columnspan=2, pady=10)

    # Crear etiqueta y campo para el nombre
    tk.Label(register_window, text="Nombre:", bg=BG_APP, font=("Shafarik", 12)).grid(row=1, column=0, pady=5, sticky="e")
    reg_entry_name = tk.Entry(register_window)
    reg_entry_name.grid(row=1, column=1, pady=5, padx=10)

    # Crear etiqueta y campo para el email
    tk.Label(register_window, text="Email:", bg=BG_APP, font=("Shafarik", 12)).grid(row=2, column=0, pady=5, sticky="e")
    reg_entry_email = tk.Entry(register_window)
    reg_entry_email.grid(row=2, column=1, pady=5, padx=10)

    # Crear etiqueta y campo para la contraseña (oculta)
    tk.Label(register_window, text="Contraseña:", bg=BG_APP, font=("Shafarik", 12)).grid(row=3, column=0, pady=5, sticky="e")
    reg_entry_password = tk.Entry(register_window, show="*")
    reg_entry_password.grid(row=3, column=1, pady=5, padx=10)

    # Crear etiqueta y campo para la ciudad por defecto
    tk.Label(register_window, text="Ciudad por defecto:", bg=BG_APP, font=("Shafarik", 12)).grid(row=4, column=0, pady=5, sticky="e")
    reg_entry_city = tk.Entry(register_window)
    reg_entry_city.grid(row=4, column=1, pady=5, padx=10)

    # Botón para completar el registro, que llama a la función register()
    tk.Button(register_window, text="Registrar", command=register, bg=BG_PANEL, font=("Shafarik", 12)).grid(row=5, column=0, columnspan=2, pady=10)

# -----------------------------------------------------------------------------
# FUNCIÓN: register()
# Objetivo: Procesar el registro de un nuevo usuario.
# Se obtienen los valores ingresados, se valida que no estén vacíos, se verifica si ya
# existe el usuario en la base de datos, se hashea la contraseña y se inserta el nuevo usuario.
# -----------------------------------------------------------------------------
def register():
    # Obtener y limpiar los datos ingresados en la ventana de registro
    nombre = reg_entry_name.get().strip()
    email = reg_entry_email.get().strip()
    contraseña = reg_entry_password.get().strip()
    ciudad_default = reg_entry_city.get().strip()

    # Validar que ningún campo esté vacío
    if not nombre or not email or not contraseña or not ciudad_default:
        messagebox.showwarning("Error", "Todos los campos son obligatorios")
        return

    try:
        # Conectar a la base de datos
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Comprobar si ya existe un usuario con el mismo email
        cursor.execute("SELECT * FROM registro WHERE email = %s", (email,))
        existing_user = cursor.fetchone()
        if existing_user:
            messagebox.showerror("Error", "El usuario ya está registrado.")
            return

        # Hashear la contraseña con bcrypt para mayor seguridad
        hashed_password = bcrypt.hashpw(contraseña.encode('utf-8'), bcrypt.gensalt())
        # Insertar el nuevo usuario en la tabla 'registro'
        cursor.execute("INSERT INTO registro (nombre, email, contraseña, default_city) VALUES (%s, %s, %s, %s)", 
                       (nombre, email, hashed_password.decode('utf-8'), ciudad_default))
        
        conn.commit()  # Confirmar los cambios en la base de datos
        messagebox.showinfo("Registro", "Usuario registrado con éxito")
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error en la base de datos: {err}")
    finally:
        # Cerrar cursor y conexión a la base de datos
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        register_window.destroy()  # Cerrar la ventana de registro

# -----------------------------------------------------------------------------
# VENTANA PRINCIPAL (LOGIN)
# -----------------------------------------------------------------------------
app = tk.Tk()
app.title("Aplicación de Registro")
app.configure(bg=BG_APP)

# Cargar y mostrar el logo en la ventana principal
logo = load_logo()
if logo:
    logo_label = tk.Label(app, image=logo, bg=BG_APP)
    logo_label.image = logo  # Guardar referencia de la imagen
    logo_label.pack(pady=10)

# Crear un frame para agrupar los campos de inicio de sesión
frame = tk.Frame(app, bg=BG_APP)
frame.pack(padx=10, pady=10)

# Etiqueta y campo para el nombre de usuario (login)
tk.Label(frame, text="Usuario:", bg=BG_APP, font=("Shafarik", 12)).grid(row=0, column=0, pady=5, sticky="e")
login_entry_username = tk.Entry(frame)
login_entry_username.grid(row=0, column=1, pady=5, padx=10)

# Etiqueta y campo para la contraseña (login)
tk.Label(frame, text="Contraseña:", bg=BG_APP, font=("Shafarik", 12)).grid(row=1, column=0, pady=5, sticky="e")
login_entry_password = tk.Entry(frame, show="*")
login_entry_password.grid(row=1, column=1, pady=5, padx=10)

# Botón para abrir la ventana de registro
tk.Button(frame, text="Registrar", command=open_register_window, bg=BG_PANEL, font=("Shafarik", 12)).grid(row=2, column=0, pady=10)

# -----------------------------------------------------------------------------
# FUNCIÓN: get_logged_user()
# Objetivo: Leer un archivo temporal (user_logged.txt) que almacena el usuario logueado.
# Si existe, se retorna el nombre y se elimina el archivo.
# -----------------------------------------------------------------------------
def get_logged_user():
    if os.path.exists("user_logged.txt"):
        with open("user_logged.txt", "r", encoding="utf-8") as f:
            username = f.read().strip()
        os.remove("user_logged.txt")  # Eliminar el archivo para evitar lecturas futuras
        return username
    return None

logged_user = get_logged_user()  # Intentar recuperar el usuario logueado

# -----------------------------------------------------------------------------
# FUNCIÓN: login()
# Objetivo: Iniciar sesión verificando las credenciales ingresadas.
# Se consulta la base de datos para obtener el hash de la contraseña y la ciudad por defecto.
# Si la autenticación es exitosa, se guarda la información en un archivo temporal y se abre
# la aplicación del clima (proyecto.py).
# -----------------------------------------------------------------------------
def login():
    nombre = login_entry_username.get().strip()
    contraseña = login_entry_password.get().strip()

    if not nombre or not contraseña:
        messagebox.showwarning("Error", "Por favor ingresa usuario y contraseña")
        return

    try:
        # Conectar a la base de datos y buscar el usuario
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        # Consultar la contraseña y la ciudad por defecto del usuario
        cursor.execute("SELECT contraseña, default_city FROM registro WHERE nombre = %s", (nombre,))
        user_data = cursor.fetchone()

        if user_data:
            stored_password = user_data[0].encode('utf-8')
            default_city = user_data[1]  # Ciudad por defecto
            # Verificar que la contraseña ingresada coincida con la almacenada (hasheada)
            if bcrypt.checkpw(contraseña.encode('utf-8'), stored_password):
                messagebox.showinfo("Inicio de Sesión", "Inicio de sesión exitoso")
                # Guardar el usuario y la ciudad por defecto en un archivo temporal separados por ";"
                with open("user_logged.txt", "w", encoding="utf-8") as f:
                    f.write(f"{nombre};{default_city}")
                # Ejecutar la aplicación del clima (proyecto.py)
                proyecto_path = os.path.join(os.path.dirname(__file__), "proyecto.py")
                subprocess.Popen(["python", proyecto_path])
                app.destroy()  # Cerrar la ventana principal de login
            else:
                messagebox.showerror("Error", "Usuario o contraseña incorrectos")
        else:
            messagebox.showerror("Error", "Usuario no encontrado")
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error: {err}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# Botón para iniciar sesión
tk.Button(frame, text="Iniciar Sesión", command=login, bg=BG_PANEL, font=("Shafarik", 12)).grid(row=2, column=1, pady=10)

# Iniciar el bucle principal de eventos de Tkinter
app.mainloop()
