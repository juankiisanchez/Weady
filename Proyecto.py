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
    # Usar la API de Restcountries para obtener la URL de la bandera
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
            flag_label.image = flag_photo  # Para mantener la referencia de la imagen
        else:
            flag_label.config(image='')  # Si no se encuentra la bandera
        
        temp_label.config(text=f"{weather_info['temp_min']}°C / {weather_info['temp_max']}°C")
        cond_label.config(text=f"{weather_info['cond']}")
        wind_label.config(text=f"{weather_info['viento']} km/h")
        humidity_label.config(text=f"{weather_info['humedad']}%")
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

# Hacer que la ventana se abra maximizada pero con la barra de título visible
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

# Dividir la pantalla
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)

left_frame = tk.Frame(main_frame, bd=2, relief=tk.SUNKEN)
left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

right_frame = tk.Frame(main_frame, bd=2, relief=tk.SUNKEN)
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

# Información de la ciudad buscada en recuadros
info_frame = tk.Frame(left_frame)
info_frame.pack(expand=True)

# Título de la ciudad seleccionada con la bandera a la izquierda
city_frame = tk.Frame(info_frame)
city_frame.pack(pady=10)

# Etiqueta para la bandera
flag_label = tk.Label(city_frame)
flag_label.pack(side=tk.LEFT, padx=10)

# Etiqueta para el nombre de la ciudad y el país
city_label = tk.Label(city_frame, text="Ciudad, País", font=("Arial", 18, "bold"))
city_label.pack(side=tk.LEFT)

# Configuración de los recuadros con bordes redondeados y sin fondo
def create_info_frame(parent, title):
    frame = tk.Frame(parent, bd=2, relief=tk.RAISED, width=400, height=250)  # Tamaño aumentado
    frame.pack_propagate(False)  # Evitar que el frame cambie su tamaño

    label_title = tk.Label(frame, text=title, font=("Arial", 16, "bold"))
    label_title.place(relx=0.5, rely=0.2, anchor="center")  # Título más grande y centrado
    label_value = tk.Label(frame, text="-", font=("Arial", 20))
    label_value.place(relx=0.5, rely=0.6, anchor="center")  # Valor más grande y centrado
    return frame, label_value

# Crear los recuadros
row1 = tk.Frame(info_frame)
row1.pack(expand=True)

temp_frame, temp_label = create_info_frame(row1, "Temperatura")
temp_frame.pack(side=tk.LEFT, padx=20, pady=20)

cond_frame, cond_label = create_info_frame(row1, "Tiempo")
cond_frame.pack(side=tk.LEFT, padx=20, pady=20)

row2 = tk.Frame(info_frame)
row2.pack(expand=True)

wind_frame, wind_label = create_info_frame(row2, "Viento")
wind_frame.pack(side=tk.LEFT, padx=20, pady=20)

humidity_frame, humidity_label = create_info_frame(row2, "Humedad")
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

# Evento para seleccionar ciudad desde la lista
def select_city(city):
    search_entry.delete(0, tk.END)
    search_entry.insert(0, city)
    update_weather_info()

# Ejecutar la aplicación
root.mainloop()