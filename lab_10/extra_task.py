import json
import os
import webbrowser
from dataclasses import dataclass

import pyaudio
import pyttsx3
import requests
import vosk


@dataclass
class Word():
    word: str
    phonetic: str
    phonetics: list[dict[str, str | dict[str, str]]]
    meanings: list[dict[str, str | list]]
    license: dict[str, str]
    sourceUrls: list[str]


def get_word(word: str):
    response = requests.get(f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}', timeout=10)
    word = response.json()[0]
    word |= {'phonetic': word['word']}
    return Word(**word)


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

tts = pyttsx3.init('sapi5')
voices = tts.getProperty('voices')
tts.setProperty('voices', 'en')
tts.setProperty(
    'voice', next(filter(lambda voice: voice.name == 'Microsoft David Desktop - English (United States)', voices)).id
)

try:
    model = vosk.Model(next(filter(lambda file_folder: 'en' in file_folder, os.listdir())))
except StopIteration:
    print('Установите модель английского языка с https://alphacephei.com/vosk/models')
    exit()
record = vosk.KaldiRecognizer(model, 16000)
pa = pyaudio.PyAudio()
stream = pa.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
output_stream = pa.open(format=pa.get_format_from_width(1), channels=1, rate=16000, output=True)
stream.start_stream()

curr_word = None

speak('Let\'s go')
print('Started 🚀')
for text in listen():
    print(text)
    if text == 'stop':
        break

    match text.split()[0]:
        case 'find':
            if len(text.split()) == 1:
                speak('Which word do you want to find?')
                continue
            curr_word = get_word(text.split()[1])
            speak('I have found a word')
        case 'meaning':
            if not curr_word:
                speak('Firstly you should say me to find new word')
            speak(curr_word.meanings[0]['definitions'][0]['definition'])
        case 'link':
            if not curr_word:
                speak('Firstly you should say me to find new word')
            speak('Let\'s look to this word in Wiktionary')
            webbrowser.open(curr_word.sourceUrls[0])
        case 'example':
            for phonetic in curr_word.phonetics:
                if 'audio' in phonetic and phonetic['audio']:
                    speak(f'Let\'s listen how {curr_word.word} sounds')
                    webbrowser.open(phonetic['audio'])
                    break
        case 'save':
            if not curr_word:
                speak('Firstly you should say me to find new word')
            speak(f'I saved the word to the file')
            with open('words.txt', 'a', encoding='utf-8') as file:
                file.write(f'{curr_word.word} is {curr_word.meanings[0]["definitions"][0]["definition"]}\n')
        case 'show':
            try:
                with open('words.txt', 'r', encoding='utf-8') as file:
                    words = file.readlines()
            except FileNotFoundError:
                speak(f'There was nothing saved yet')
                continue

            if not words:
                speak(f'There was nothing saved yet')
                continue
            speak(f'Look, which word I saved')
            for word in words:
                speak(word)
