import os
import ctypes
import tkinter as tk
import tkinter.ttk as ttk
import subprocess
import requests
import threading
from PIL import Image, ImageTk, ImageOps
from io import BytesIO

# -------------------------------------------------------------------------
# DEFINICIÓN DE COLORES
# -------------------------------------------------------------------------
BG_APP = "#FB8C00"       # Fondo general para la sección izquierda
BG_PANEL = "#FFCC80"     # Fondo de los recuadros y botones (sección izquierda)

# -------------------------------------------------------------------------
# DEFINICIÓN DEL API
# -------------------------------------------------------------------------
API_KEY = "13664056350383ee5b2ed74523f41ff1"  # Reemplaza con tu clave de API
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

# -------------------------------------------------------------------------
# Función para oscurecer un color (se usa en la animación)
# -------------------------------------------------------------------------
def darken_color(hex_color, factor=0.95):
    hex_color = hex_color.lstrip('#')
    r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    r = max(0, min(255, int(r * factor)))
    g = max(0, min(255, int(g * factor)))
    b = max(0, min(255, int(b * factor)))
    return f"#{r:02x}{g:02x}{b:02x}"

# -------------------------------------------------------------------------
# 1) Función para cargar fuentes TTF de forma temporal en Windows
# -------------------------------------------------------------------------
def load_custom_font(font_file):
    if os.name == "nt":
        font_path = os.path.abspath(font_file)
        FR_PRIVATE = 0x10
        num_fonts = ctypes.windll.gdi32.AddFontResourceExW(font_path, FR_PRIVATE, 0)
        if num_fonts == 0:
            print("Error al cargar la fuente:", font_file)
        else:
            print("Fuente cargada correctamente:", font_file)
    else:
        print("Carga dinámica de fuentes TTF no implementada para este sistema.")

# -------------------------------------------------------------------------
# 2) Carga de fuentes: Pacifico y Shafarik
# -------------------------------------------------------------------------
current_dir = os.path.dirname(os.path.abspath(__file__))
font_pacifico = os.path.join(current_dir, "../Resources/Fonts/Pacifico-Regular.ttf")
font_shafarik = os.path.join(current_dir, "../Resources/Fonts/Shafarik-Regular.ttf")
load_custom_font(font_pacifico)
load_custom_font(font_shafarik)

# -------------------------------------------------------------------------
# 3) Función para dibujar un rectángulo redondeado en un canvas
# -------------------------------------------------------------------------
def round_rectangle(canvas, x1, y1, x2, y2, radius=25, **kwargs):
    points = [
        x1 + radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1
    ]
    return canvas.create_polygon(points, **kwargs, smooth=True)

# -------------------------------------------------------------------------
# 4) Función para crear un frame con fondo redondeado (barra lateral)
# -------------------------------------------------------------------------
def create_rounded_frame(parent, radius=25, bg_color="#333333", width=300):
    canvas = tk.Canvas(parent, bg=parent["bg"], highlightthickness=0, width=width)
    inner_frame = tk.Frame(canvas, bg=bg_color)
    def on_resize(event):
        canvas.delete("all")
        w = event.width
        h = event.height
        round_rectangle(canvas, 0, 0, w, h, radius=radius, fill=bg_color, outline="")
        canvas.create_window(radius/2, radius/2, window=inner_frame, anchor="nw", width=w - radius, height=h - radius)
    canvas.bind("<Configure>", on_resize)
    return canvas, inner_frame

# -------------------------------------------------------------------------
# 5) Función para reescalar imágenes manteniendo la proporción
# -------------------------------------------------------------------------
def load_icon(source, size=(50, 50)):
    try:
        if source.startswith("http"):
            response = requests.get(source)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content))
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
            full_path = os.path.join(base_path, source)
            img = Image.open(full_path)
        img = ImageOps.contain(img, size)
        return ImageTk.PhotoImage(img)
    except Exception as e:
        print("Error al cargar la imagen:", e)
        return None

# -------------------------------------------------------------------------
# 6) Función para obtener el ícono del estado del tiempo
# -------------------------------------------------------------------------
def get_weather_icon(condition):
    condition = condition.lower().strip()
    mapping = {
        "cielo claro": "clear",
        "nubes": "clouds",
        "algo de nubes": "clouds",
        "nubes dispersas": "clouds",
        "nublado": "clouds",
        "muy nuboso": "clouds",
        "lluvia ligera": "rain",
        "lluvia moderada": "rain",
        "lluvia intensa": "rain",
        "tormenta eléctrica": "thunderstorm",
        "llovizna": "drizzle",
        "llovizna ligera": "drizzle",
        "niebla": "mist",
        "neblina": "mist",
        "nieve ligera": "snow",
        "nieve moderada": "snow",
        "nevada intensa": "snow",
        "granizo": "thunderstorm"
    }
    key = mapping.get(condition, "clear")
    icon_map = {
        "clear": "../imagenes/soleado.png",
        "clouds": "../imagenes/nubes.png",
        "rain": "../imagenes/lluvia.png",
        "thunderstorm": "../imagenes/tormenta.png",
        "drizzle": "../imagenes/llovizna.png",
        "mist": "../imagenes/niebla.png",
        "snow": "../imagenes/nieve.png"
    }
    return load_icon(icon_map[key])

# -------------------------------------------------------------------------
# 7) Función fetch_weather para obtener datos del API
# -------------------------------------------------------------------------
def fetch_weather(city):
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",
        "lang": "es"
    }
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        return {
            "temp_min": round(data["main"]["temp_min"]),
            "temp_max": round(data["main"]["temp_max"]),
            "cond": data["weather"][0]["description"].capitalize(),
            "viento": round(data["wind"]["speed"]),
            "humedad": data["main"]["humidity"],
            "city": data["name"],
            "country": data["sys"]["country"],
            "country_code": data["sys"]["country"].lower()
        }
    except requests.exceptions.RequestException:
        return None

# -------------------------------------------------------------------------
# 8) Función fetch_flag para obtener la bandera de un país
# -------------------------------------------------------------------------
def fetch_flag(country_code):
    flag_url = f"https://restcountries.com/v3.1/alpha/{country_code}"
    try:
        response = requests.get(flag_url)
        response.raise_for_status()
        country_data = response.json()
        flag_url = country_data[0]["flags"]["png"]
        flag_img = Image.open(BytesIO(requests.get(flag_url).content))
        return flag_img
    except requests.exceptions.RequestException:
        return None

# -------------------------------------------------------------------------
# 9) Función para crear el canvas de información del tiempo
# -------------------------------------------------------------------------
def create_info_canvas(parent, title):
    canvas = tk.Canvas(parent, width=400, height=250, highlightthickness=0, bg=parent.cget("bg"))
    round_rectangle(canvas, 10, 10, 390, 240, radius=20, fill=BG_PANEL, outline="")
    label_title = tk.Label(canvas, text=title, font=("Pacifico", 16), bg=BG_PANEL)
    canvas.create_window(200, 50, window=label_title)
    icon_label = tk.Label(canvas, bg=BG_PANEL)
    canvas.create_window(200, 110, window=icon_label)
    label_value = tk.Label(canvas, text="-", font=("Shafarik", 20), bg=BG_PANEL)
    canvas.create_window(200, 190, window=label_value)
    return canvas, icon_label, label_value

# -------------------------------------------------------------------------
# 10) Función animate_press: animación al pulsar (reduce tamaño, oscurece y reduce fuente)
# -------------------------------------------------------------------------
def animate_press(canvas, center, down_scale=0.95, duration=100, rect_id=None, original_color=None):
    # Reducir tamaño del botón (todo el canvas)
    canvas.scale("all", center[0], center[1], down_scale, down_scale)
    # Oscurecer el fondo (si se proporciona rect_id y original_color)
    if rect_id is not None and original_color is not None:
        dark_color = darken_color(original_color, factor=0.95)
        canvas.itemconfig(rect_id, fill=dark_color)
    # Reducir también el tamaño de la fuente del texto
    if hasattr(canvas, "text_id") and hasattr(canvas, "original_font"):
        font_family, font_size = canvas.original_font
        smaller_font = (font_family, max(1, int(font_size * down_scale)))
        canvas.itemconfig(canvas.text_id, font=smaller_font)
    # Después de 'duration' milisegundos, restaurar tamaño, color y fuente
    canvas.after(duration, lambda: (
        canvas.scale("all", center[0], center[1], 1/down_scale, 1/down_scale),
        canvas.itemconfig(rect_id, fill=original_color) if rect_id is not None and original_color is not None else None,
        canvas.itemconfig(canvas.text_id, font=canvas.original_font) if hasattr(canvas, "text_id") else None
    ))

# -------------------------------------------------------------------------
# 11) Función para crear botones redondeados con opción de imagen y efecto de presionar
# -------------------------------------------------------------------------
def create_rounded_button(parent, text, command, width=250, height=40, radius=20, 
                           bg=BG_PANEL, fg="black", active_bg=BG_PANEL, font=("Shafarik", 12), image=None):
    canvas = tk.Canvas(parent, width=width, height=height, bg=parent.cget("bg"), highlightthickness=0)
    rect = round_rectangle(canvas, 0, 0, width, height, radius=radius, fill=bg, outline="")
    original_color = bg
    # Guardamos la fuente original en el canvas
    canvas.original_font = font
    if image is not None:
        # Dibujar la imagen a la izquierda y luego el texto a la derecha
        img_id = canvas.create_image(10, height//2, image=image, anchor="w")
        text_id = canvas.create_text(10 + image.width() + 5, height//2, text=text, fill=fg, font=font, anchor="w")
        canvas.image = image  # Referencia para evitar recolección
    else:
        text_id = canvas.create_text(width//2, height//2, text=text, fill=fg, font=font)
    # Guardamos el id del texto para poder modificar su fuente en la animación
    canvas.text_id = text_id
    def on_click(event):
        center = (width//2, height//2)
        animate_press(canvas, center, down_scale=0.95, duration=100, rect_id=rect, original_color=original_color)
        threading.Thread(target=command).start()
    canvas.bind("<Button-1>", on_click)
    def on_enter(event):
        canvas.itemconfig(rect, fill=active_bg)
    def on_leave(event):
        canvas.itemconfig(rect, fill=bg)
    canvas.bind("<Enter>", on_enter)
    canvas.bind("<Leave>", on_leave)
    return canvas

def create_city_button(parent, city, country):
    btn = create_rounded_button(parent, f"{city}, {country}", command=lambda: select_city(city))
    btn.pack(fill=tk.X, padx=10, pady=10)

# -------------------------------------------------------------------------
# 12) Función para actualizar la información de la ciudad (async)
# -------------------------------------------------------------------------
def update_weather_info():
    city = search_entry.get()
    def task():
        weather_info = fetch_weather(city)
        root.after(0, lambda: update_ui(weather_info))
    threading.Thread(target=task).start()

def update_ui(weather_info):
    if weather_info:
        city_label.config(text=f"{weather_info['city']}, {weather_info['country']}")
        flag_img = fetch_flag(weather_info['country_code'])
        if flag_img:
            flag_img = flag_img.resize((50, 30))
            flag_photo = ImageTk.PhotoImage(flag_img)
            flag_label.config(image=flag_photo)
            flag_label.image = flag_photo
        else:
            flag_label.config(image='')
        if weather_info['temp_min'] > 17:
            temp_icon = load_icon("../imagenes/alta-temperatura.png")
        else:
            temp_icon = load_icon("../imagenes/baja-temperatura.png")
        temp_label.config(text=f"{weather_info['temp_min']}°C / {weather_info['temp_max']}°C")
        temp_icon_label.config(image=temp_icon)
        temp_icon_label.image = temp_icon
        weather_icon = get_weather_icon(weather_info['cond'])
        cond_label.config(text=f"{weather_info['cond']}")
        cond_icon_label.config(image=weather_icon)
        cond_icon_label.image = weather_icon
        wind_icon = load_icon("https://cdn-icons-png.flaticon.com/512/11742/11742598.png")
        wind_label.config(text=f"{weather_info['viento']} km/h")
        wind_icon_label.config(image=wind_icon)
        wind_icon_label.image = wind_icon
        humidity_icon = load_icon("https://cdn-icons-png.flaticon.com/512/1582/1582886.png")
        humidity_label.config(text=f"{weather_info['humedad']}%")
        humidity_icon_label.config(image=humidity_icon)
        humidity_icon_label.image = humidity_icon
    else:
        city_label.config(text="Ciudad no encontrada")
        flag_label.config(image='')
        temp_label.config(text="-")
        cond_label.config(text="-")
        wind_label.config(text="-")
        humidity_label.config(text="-")

# -------------------------------------------------------------------------
# 13) Función para ejecutar registro.py (Login)
# -------------------------------------------------------------------------
def run_registro():
    registro_path = os.path.join(os.path.dirname(__file__), "registro.py")
    subprocess.Popen(["python", registro_path])

# -------------------------------------------------------------------------
# 14) Configuración de la ventana principal e interfaz usando grid
# -------------------------------------------------------------------------
root = tk.Tk()
root.title("Aplicación del Tiempo")
root.configure(bg=BG_APP)

root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=0)
root.grid_columnconfigure(2, weight=1)
root.grid_rowconfigure(0, weight=0)   # Barra de búsqueda
root.grid_rowconfigure(1, weight=0)   # Separador horizontal
root.grid_rowconfigure(2, weight=1)   # Información

# --- Columna izquierda ---
# Fila 0: Barra de búsqueda.
search_frame = tk.Frame(root, bg=BG_APP)
search_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

# Frame interno para agrupar elementos de búsqueda a la izquierda.
search_left_frame = tk.Frame(search_frame, bg=BG_APP)
search_left_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

search_label = tk.Label(search_left_frame, text="Buscar ciudad:", bg=BG_APP, font=("Shafarik", 10, "bold"))
search_label.pack(side=tk.LEFT, padx=5)

search_entry = tk.Entry(search_left_frame, width=30, font=("Shafarik", 10))
search_entry.pack(side=tk.LEFT, padx=5)

search_button = create_rounded_button(
    search_left_frame,
    "Buscar",
    command=update_weather_info,
    width=80,
    height=25,
    radius=10,
    font=("Shafarik", 10)
)
search_button.pack(side=tk.LEFT, padx=5)

# Botón de login a la derecha del todo en la barra.
icono_usuario = load_icon("../imagenes/icono_usuario.png", size=(20, 20))
login_button = create_rounded_button(
    search_frame,
    "Login",
    command=lambda: threading.Thread(target=run_registro).start(),
    width=80,
    height=25,
    radius=10,
    font=("Shafarik", 10),
    image=icono_usuario
)
login_button.pack(side=tk.RIGHT, padx=5)

# Fila 1: Separador horizontal en la columna izquierda.
h_sep = ttk.Separator(root, orient="horizontal")
h_sep.grid(row=1, column=0, sticky="ew", padx=10)

# Fila 2: Sección izquierda (información de la ciudad).
info_frame = tk.Frame(root, bg=BG_APP)
info_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

city_frame = tk.Frame(info_frame, bg=BG_APP)
city_frame.pack(pady=10)

flag_label = tk.Label(city_frame, bg=BG_APP)
flag_label.pack(side=tk.LEFT, padx=10)

city_label = tk.Label(city_frame, text="Ciudad, País", font=("Pacifico", 18), bg=BG_APP)
city_label.pack(side=tk.LEFT)

row1 = tk.Frame(info_frame, bg=BG_APP)
row1.pack(expand=True)

temp_canvas, temp_icon_label, temp_label = create_info_canvas(row1, "Temperatura")
temp_canvas.pack(side=tk.LEFT, padx=20, pady=20)

cond_canvas, cond_icon_label, cond_label = create_info_canvas(row1, "Tiempo")
cond_canvas.pack(side=tk.LEFT, padx=20, pady=20)

row2 = tk.Frame(info_frame, bg=BG_APP)
row2.pack(expand=True)

wind_canvas, wind_icon_label, wind_label = create_info_canvas(row2, "Viento")
wind_canvas.pack(side=tk.LEFT, padx=20, pady=20)

humidity_canvas, humidity_icon_label, humidity_label = create_info_canvas(row2, "Humedad")
humidity_canvas.pack(side=tk.LEFT, padx=20, pady=20)

# --- Columna separadora: Vertical ---
v_sep = ttk.Separator(root, orient="vertical")
v_sep.grid(row=0, column=1, rowspan=3, sticky="ns", padx=5)

# --- Columna derecha (barra lateral) ---
right_canvas, right_frame = create_rounded_frame(root, radius=25, bg_color="#333333", width=300)
right_canvas.grid(row=0, column=2, rowspan=3, sticky="nsew", padx=10, pady=10)

predefined_label = tk.Label(right_frame, text="Ciudades principales:", font=("Pacifico", 14), bg="#333333", fg="white")
predefined_label.pack(anchor="center", pady=10)

predefined_cities = [
    ("Nueva York", "EE.UU."),
    ("Madrid", "España"),
    ("Tokio", "Japón"),
    ("Londres", "Reino Unido"),
    ("Sídney", "Australia")
]

for city, country in predefined_cities:
    create_city_button(right_frame, city, country)

def select_city(city):
    search_entry.delete(0, tk.END)
    search_entry.insert(0, city)
    update_weather_info()

root.mainloop()
