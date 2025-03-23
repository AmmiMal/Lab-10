import json, requests
import os

import pyttsx3, pyaudio, vosk, webbrowser
from vosk import KaldiRecognizer


class VoiceAssistant:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.tts = pyttsx3.init('sapi5')

        model_folder = r"C:\Users\mi\Downloads\vosk-model-small-en-us-0.15"
        self.model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), model_folder)

        if not os.path.exists(self.model_path):
            print(f"Model {self.model_path} was not found.")
            exit(1)

        self.model = vosk.Model(self.model_path)
        self.rec = KaldiRecognizer(self.model, 16000)
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
        self.stream.start_stream()

    def find_word_meaning(self, word):
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return None

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def save_data(self, data):
        with open("saved_data.txt", "a") as file:
            file.write(data + "\n")
        self.speak("Data saved successfully.")

    def process_command(self, command):
        if command.startswith("find"):
            word = command.split("find")[1].strip()
            self.cur_word = word
            self.meaning_of_word = self.find_word_meaning(word)
            if self.meaning_of_word:
                self.speak(f"The word {self.cur_word} is found. Please, tell me what you want to know about it:"
                      f" 'meaning', 'link' or 'save'.")
            else:
                self.speak("Please first say the word you want to know, like 'find word'.")

        elif command == "save":
            self.speak("Saving your data...")
            if self.cur_word:
                self.save_data(self.cur_word)
            else:
                self.speak("Please first say the word you want to know, like 'find word'.")
        elif command == "meaning":
            if self.meaning_of_word:
                meanings = self.meaning_of_word[0]['meanings']
                for meaning in meanings:
                    part_of_speech = meaning['partOfSpeech']
                    definition = meaning['definitions'][0]['definition']
                    self.speak(f"{self.cur_word}, {part_of_speech}: {definition}")
            else:
                self.speak("Please first say the word you want to know, like 'find word'.")

        elif command.startswith("link"):
            if self.cur_word:
                url = f"https://dictionary.cambridge.org/dictionary/english/{self.cur_word}"
                webbrowser.open(url)
                self.speak(f"Opening information in your browser.")
            else:
                self.speak("Please first say the word you want to know , like 'find word'.")

        elif command == "example":
            self.speak("Here is an example: 'find hedgehog'")
        elif command == "exit":
            self.speak("Completing the work... Bye!")
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()
        else:
            self.speak("Sorry, I don't understand that command.")

    def start(self):
        print("Listening...")
        while True:
            data = self.stream.read(4096, exception_on_overflow=False)
            if self.rec.AcceptWaveform(data):
                result = self.rec.Result()
                result_dict = json.loads(result)
                command = result_dict.get("text", "").strip().lower()
                if command:
                    print(f"Command: {command}")
                    self.process_command(command)
                else:
                    print("No command recognized.")
            else:
                partial_result = self.rec.PartialResult()
                print(partial_result)


if __name__ == '__main__':
    assistant = VoiceAssistant()
    assistant.start()
