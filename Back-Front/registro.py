import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import mysql.connector
import bcrypt

# Configuración de la conexión a la base de datos
db_config = {
    'user': 'root',
    'password': '1234',
    'host': 'localhost',
    'database': 'weady'  # Asegúrate de que este nombre sea el correcto
}

# Cargar el logo
def load_logo():
    try:
        image = Image.open("imagenes/logo.png")  # Asegúrate de que el logo esté en el mismo directorio
        image = image.resize((150, 150))  # Redimensionar si es necesario
        return ImageTk.PhotoImage(image)
    except Exception as e:
        print(f"Error al cargar el logo: {e}")
        return None

# Función para abrir la ventana de registro
def open_register_window():
    register_window = tk.Toplevel(app)
    register_window.title("Registro")

    logo = load_logo()
    if logo:
        logo_label = tk.Label(register_window, image=logo)
        logo_label.image = logo  # Guardar referencia para evitar que se elimine
        logo_label.grid(row=0, column=0, columnspan=2, pady=10)

    tk.Label(register_window, text="Nombre:").grid(row=1, column=0, pady=5)
    entry_name = tk.Entry(register_window)
    entry_name.grid(row=1, column=1, pady=5)

    tk.Label(register_window, text="Email:").grid(row=2, column=0, pady=5)
    entry_email = tk.Entry(register_window)
    entry_email.grid(row=2, column=1, pady=5)

    tk.Label(register_window, text="Contraseña:").grid(row=3, column=0, pady=5)
    entry_password = tk.Entry(register_window, show="*")
    entry_password.grid(row=3, column=1, pady=5)

    def register():
        nombre = entry_name.get().strip()
        email = entry_email.get().strip()
        contraseña = entry_password.get().strip()

        if not nombre or not email or not contraseña:
            messagebox.showwarning("Error", "Todos los campos son obligatorios")
            return

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            # Comprobar si el usuario ya está registrado
            cursor.execute("SELECT * FROM registro WHERE email = %s", (email,))
            existing_user = cursor.fetchone()
            if existing_user:
                messagebox.showerror("Error", "El usuario ya está registrado.")
                return

            hashed_password = bcrypt.hashpw(contraseña.encode('utf-8'), bcrypt.gensalt())
            cursor.execute("INSERT INTO registro (nombre, email, contraseña) VALUES (%s, %s, %s)", 
                        (nombre, email, hashed_password.decode('utf-8')))
            
            conn.commit()
            messagebox.showinfo("Registro", "Usuario registrado con éxito")
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error en la base de datos: {err}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
            register_window.destroy()

    tk.Button(register_window, text="Registrar", command=register).grid(row=4, column=0, columnspan=2, pady=10)

# Ventana principal
app = tk.Tk()
app.title("Aplicación de Registro")

# Cargar y mostrar el logo en la pantalla principal
logo = load_logo()
if logo:
    logo_label = tk.Label(app, image=logo)
    logo_label.image = logo  # Guardar referencia correctamente
    logo_label.pack(pady=10)

frame = tk.Frame(app)
frame.pack(padx=10, pady=10)

tk.Label(frame, text="Usuario:").grid(row=0, column=0, pady=5)
entry_username = tk.Entry(frame)
entry_username.grid(row=0, column=1, pady=5)

tk.Label(frame, text="Contraseña:").grid(row=1, column=0, pady=5)
entry_password = tk.Entry(frame, show="*")
entry_password.grid(row=1, column=1, pady=5)

tk.Button(frame, text="Registrar", command=open_register_window).grid(row=2, column=0, pady=10)

# Función para iniciar sesión
def login():
    nombre = entry_username.get().strip()
    contraseña = entry_password.get().strip()

    if not nombre or not contraseña:
        messagebox.showwarning("Error", "Por favor ingresa usuario y contraseña")
        return

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT contraseña FROM registro WHERE nombre = %s", (nombre,))
        user_data = cursor.fetchone()

        if user_data:
            stored_password = user_data[0].encode('utf-8')  
            if bcrypt.checkpw(contraseña.encode('utf-8'), stored_password):
                messagebox.showinfo("Inicio de Sesión", "Inicio de sesión exitoso")
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

tk.Button(frame, text="Iniciar Sesión", command=login).grid(row=2, column=1, pady=10)

app.mainloop()
