import os
import tkinter as tk
from tkinter import ttk
import requests
from PIL import Image, ImageTk
from io import BytesIO

# Configuración del API
API_KEY = "13664056350383ee5b2ed74523f41ff1"  # Reemplaza con tu clave de API de OpenWeatherMap
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

# Función para obtener datos meteorológicos reales
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
        weather_info = {
            "temp_min": round(data["main"]["temp_min"]),
            "temp_max": round(data["main"]["temp_max"]),
            "cond": data["weather"][0]["description"].capitalize(),
            "viento": round(data["wind"]["speed"]),
            "humedad": data["main"]["humidity"],
            "city": data["name"],
            "country": data["sys"]["country"],
            "country_code": data["sys"]["country"].lower()  # Código de país en minúsculas
        }
        return weather_info
    except requests.exceptions.RequestException:
        return None

# Función para obtener la bandera del país
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

# Función para cargar un icono desde una URL o ruta local
def load_icon(source, size=(50, 50)):
    try:
        if source.startswith("http"):
            response = requests.get(source)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content))
        else:
            # Construir la ruta absoluta basada en la ubicación del script
            base_path = os.path.dirname(os.path.abspath(__file__))
            full_path = os.path.join(base_path, source)
            img = Image.open(full_path)
        img = img.resize(size)
        return ImageTk.PhotoImage(img)
    except Exception as e:
        print("Error al cargar la imagen:", e)
        return None

# Función para obtener el icono del estado del tiempo según el texto recibido de la API
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
        "clear": "../imagenes/soleado.png",         # Sol
        "clouds": "../imagenes/nubes.png",            # Nubes
        "rain": "../imagenes/lluvia.png",              # Lluvia
        "thunderstorm": "../imagenes/tormenta.png",    # Tormenta
        "drizzle": "../imagenes/llovizna.png",         # Llovizna
        "mist": "../imagenes/niebla.png",              # Niebla
        "snow": "../imagenes/nieve.png"                # Nieve
    }
    return load_icon(icon_map[key])

# Función para actualizar la información de la ciudad buscada
def update_weather_info():
    city = search_entry.get()
    weather_info = fetch_weather(city)
    if weather_info:
        city_label.config(text=f"{weather_info['city']}, {weather_info['country']}")
        # Actualizar bandera
        flag_img = fetch_flag(weather_info['country_code'])
        if flag_img:
            flag_img = flag_img.resize((50, 30))  # Ajustar tamaño
            flag_photo = ImageTk.PhotoImage(flag_img)
            flag_label.config(image=flag_photo)
            flag_label.image = flag_photo  # Mantener referencia
        else:
            flag_label.config(image='')
        
        # Actualizar iconos y valores
        # Determinar el icono según la temperatura mínima y máxima
        if weather_info['temp_min'] > 17:
            temp_icon = load_icon("../imagenes/alta-temperatura.png")  # Alta temperatura
        else:
            temp_icon = load_icon("../imagenes/baja-temperatura.png")  # Baja temperatura

        # Actualizar el texto y el icono en el label
        temp_label.config(text=f"{weather_info['temp_min']}°C / {weather_info['temp_max']}°C")
        temp_icon_label.config(image=temp_icon)
        temp_icon_label.image = temp_icon

        weather_icon = get_weather_icon(weather_info['cond'])
        cond_label.config(text=f"{weather_info['cond']}")
        cond_icon_label.config(image=weather_icon)
        cond_icon_label.image = weather_icon

        wind_icon = load_icon("https://cdn-icons-png.flaticon.com/512/11742/11742598.png")  # Viento
        wind_label.config(text=f"{weather_info['viento']} km/h")
        wind_icon_label.config(image=wind_icon)
        wind_icon_label.image = wind_icon

        humidity_icon = load_icon("https://cdn-icons-png.flaticon.com/512/1582/1582886.png")  # Humedad
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

# Configuración de la ventana principal
root = tk.Tk()
root.title("Aplicación del Tiempo")
root.state('zoomed')

# Barra de búsqueda
search_frame = tk.Frame(root)
search_frame.pack(side=tk.TOP, anchor="nw", padx=10, pady=10)

search_label = tk.Label(search_frame, text="Buscar ciudad:")
search_label.pack(side=tk.LEFT, padx=5)

search_entry = tk.Entry(search_frame, width=30)
search_entry.pack(side=tk.LEFT, padx=5)

search_button = tk.Button(search_frame, text="Buscar", command=update_weather_info)
search_button.pack(side=tk.LEFT, padx=5)

# Dividir la pantalla en dos secciones: información principal y ciudades predefinidas
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)

left_frame = tk.Frame(main_frame, bd=2, relief=tk.SUNKEN)
left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

right_frame = tk.Frame(main_frame, bd=2, relief=tk.SUNKEN)
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

# Información de la ciudad buscada
info_frame = tk.Frame(left_frame)
info_frame.pack(expand=True)

city_frame = tk.Frame(info_frame)
city_frame.pack(pady=10)

flag_label = tk.Label(city_frame)
flag_label.pack(side=tk.LEFT, padx=10)

city_label = tk.Label(city_frame, text="Ciudad, País", font=("Arial", 18, "bold"))
city_label.pack(side=tk.LEFT)

# Función para crear recuadros de información (Temperatura, Tiempo, Viento, Humedad)
def create_info_frame(parent, title):
    frame = tk.Frame(parent, bd=2, relief=tk.RAISED, width=400, height=250)
    frame.pack_propagate(False)
    label_title = tk.Label(frame, text=title, font=("Arial", 16, "bold"))
    label_title.place(relx=0.5, rely=0.2, anchor="center")
    icon_label = tk.Label(frame)
    icon_label.place(relx=0.5, rely=0.45, anchor="center")
    label_value = tk.Label(frame, text="-", font=("Arial", 20))
    label_value.place(relx=0.5, rely=0.75, anchor="center")
    return frame, icon_label, label_value

# Crear recuadros de información
row1 = tk.Frame(info_frame)
row1.pack(expand=True)

temp_frame, temp_icon_label, temp_label = create_info_frame(row1, "Temperatura")
temp_frame.pack(side=tk.LEFT, padx=20, pady=20)

cond_frame, cond_icon_label, cond_label = create_info_frame(row1, "Tiempo")
cond_frame.pack(side=tk.LEFT, padx=20, pady=20)

row2 = tk.Frame(info_frame)
row2.pack(expand=True)

wind_frame, wind_icon_label, wind_label = create_info_frame(row2, "Viento")
wind_frame.pack(side=tk.LEFT, padx=20, pady=20)

humidity_frame, humidity_icon_label, humidity_label = create_info_frame(row2, "Humedad")
humidity_frame.pack(side=tk.LEFT, padx=20, pady=20)

# Lista de ciudades predefinidas
def create_city_button(parent, city, country):
    button = tk.Button(parent, text=f"{city}, {country}", font=("Arial", 12), command=lambda: select_city(city))
    button.pack(fill=tk.X, padx=5, pady=5)

predefined_label = tk.Label(right_frame, text="Ciudades principales:", font=("Arial", 14))
predefined_label.pack(anchor="w", pady=10)

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
