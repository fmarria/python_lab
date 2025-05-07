import json
import os
import pip
from dataclasses import dataclass

import pyaudio
try:
    import pymorphy2
except ImportError:
    pip.main(['install', 'pymorphy2'])
    import pymorphy2
import pyttsx3
import requests
try:
    import translators as ts
except ImportError:
    pip.main(['install', 'translators'])
    import translators as ts
import vosk


@dataclass
class Activity():
    activity: str
    type: str
    participants: int
    price: float
    link: str
    key: str
    accessibility: float


def get_activity():
    response = requests.get('https://www.boredapi.com/api/activity', timeout=10)
    activity = Activity(**response.json())
    activity.activity = ts.translate_text(activity.activity, to_language='ru')
    return activity


def listen():
    while True:
        data = stream.read(4000, exception_on_overflow=False)
        if record.AcceptWaveform(data) and len(data) > 0:
            answer = json.loads(record.Result())
            if answer['text']:
                yield answer['text']


def speak(say):
    tts.say(say)
    tts.runAndWait()

try:
    morph = pymorphy2.MorphAnalyzer(lang='ru')
except ValueError:
    pip.main(['install', 'pymorphy2-dicts-ru'])
    morph = pymorphy2.MorphAnalyzer(lang='ru')
tts = pyttsx3.init('sapi5')
voices = tts.getProperty('voices')
tts.setProperty('voices', 'ru')
tts.setProperty('voice', next(filter(lambda voice: 'ru' in voice.name.lower(), voices)).id)

try:
    model = vosk.Model(next(filter(lambda file_folder: 'ru' in file_folder, os.listdir())))
except StopIteration:
    print('Установите модель русского языка с https://alphacephei.com/vosk/models')
    exit()
record = vosk.KaldiRecognizer(model, 16000)
pa = pyaudio.PyAudio()
stream = pa.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
stream.start_stream()

curr_activity = get_activity()

speak('Поехали')
print('Запущен 🚀')
for text in listen():
    print(text)
    text = morph.parse(text)[0].normal_form
    if text == 'стоп':
        break

    match text:
        case 'новый':
            speak('Теперь тебе есть чем заняться')
            curr_activity = get_activity()
        case 'название':
            speak(curr_activity.activity)
        case 'участник':
            speak(f'Нужно {curr_activity.participants} человек')
        case 'сохранить':
            speak(f'Сохранила в файлик')
            with open('tasks.txt', 'a', encoding='utf-8') as file:
                file.write(f'{curr_activity.activity} для {curr_activity.participants} человек ценой в {curr_activity.price} долларов\n')
        case 'показать':
            try:
                with open('tasks.txt', 'r', encoding='utf-8') as file:
                    tasks = file.readlines()
            except FileNotFoundError:
                speak(f'Пока ещё ничего не сохранено')
                continue

            if not tasks:
                speak(f'Пока ещё ничего не сохранено')
                continue
            speak(f'Смотри, что я сохранила из занятий')
            for task in tasks:
                speak(task)
