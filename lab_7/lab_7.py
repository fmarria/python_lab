import requests
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
#task 1
city_name = 'Moscow'
weather_api_key = '64bccd5fd02857b50f39facbeba7094f'

weather_url = f'http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={weather_api_key}&units=metric'
response = requests.get(weather_url)
weather_data = response.json()

description = weather_data['weather'][0]['description']
humidity = weather_data['main']['humidity']
pressure = weather_data['main']['pressure']

print(f'!Задание 1: Погода в {city_name}')
print(f'Описание: {description}')
print(f'Влажность: {humidity}%')
print(f'Давление: {pressure} гПа')
print()

# task 2
print('!Задание 2: Rick and Morty: Первые 5 персонажей')
url = 'https://rickandmortyapi.com/api/character'  # Базовый URL API

response = requests.get(url)
data = response.json()

if response.status_code == 200:
    characters = data['results'][:5]
    for character in characters:
        print(f"Имя: {character['name']}")
        print(f"Статус: {character['status']}")
        print(f"Вид: {character['species']}")
        print(f"Пол: {character['gender']}")
        print(f"Локация: {character['location']['name']}")
        print(f"Создан: {character['created']}")
        print('...' * 10)
else:
    print(f"Ошибка {response.status_code}: {data.get('error', 'Неизвестная ошибка')}")
print()

#additional task
def get_random_fox_image_url():
    response = requests.get("https://randomfox.ca/floof/")
    if response.status_code == 200:
        data = response.json()
        return data['image']
    else:
        print("Ошибка при получении изображения")
        return None

def update_image():
    global image_label, current_image
    image_url = get_random_fox_image_url()
    if image_url:
        image_data = requests.get(image_url, stream=True)
        if image_data.status_code == 200:
            image = Image.open(image_data.raw)
            image = image.resize((400, 400), Image.ANTIALIAS)
            current_image = ImageTk.PhotoImage(image)
            image_label.config(image=current_image)

root = tk.Tk()
root.title("!Задание 3: Генератор картинок лис")
root.geometry("500x500")
current_image = None
image_label = tk.Label(root)
image_label.pack(pady=20)
update_button = ttk.Button(root, text="Следующая картинка", command=update_image)
update_button.pack(pady=10)
update_image()
root.mainloop()