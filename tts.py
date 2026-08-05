import pyttsx3

engine = pyttsx3.init()

def speak(text):
    engine.stop()      # hentikan suara sebelumnya
    engine.say(text)
    engine.runAndWait()

def stop():
    engine.stop()