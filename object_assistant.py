import streamlit as st
import cv2
import numpy as np
from ultralytics import YOLO
import time
import threading
from gtts import gTTS
import pygame
import os
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase

# =========================
# AUDIO INIT (ANTI CRASH)
# =========================
if not pygame.mixer.get_init():
    pygame.mixer.init()

audio_lock = threading.Lock()

def speak(text):
    """Text-to-speech aman (no overlap)"""
    def run():
        with audio_lock:
            try:
                filename = f"voice_{int(time.time()*1000)}.mp3"

                tts = gTTS(text=text, lang='id')
                tts.save(filename)

                pygame.mixer.music.load(filename)
                pygame.mixer.music.play()

                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)

                pygame.mixer.music.stop()
                pygame.mixer.music.unload()

                if os.path.exists(filename):
                    os.remove(filename)

            except Exception as e:
                print("Audio error:", e)

    threading.Thread(target=run, daemon=True).start()

# =========================
# LOAD MODEL (CACHE)
# =========================
@st.cache_resource
def load_model():
    return YOLO("yolov8n.pt")

model = load_model()

# =========================
# LABEL INDONESIA
# =========================
class_names = {
    'person': 'orang',
    'bicycle': 'sepeda',
    'car': 'mobil',
    'motorcycle': 'motor',
    'bus': 'bus',
    'truck': 'truk',
    'chair': 'kursi',
    'bottle': 'botol',
    'cup': 'gelas',
    'cell phone': 'handphone',
    'laptop': 'laptop',
    'book': 'buku',
    'tv': 'televisi',
    'dog': 'anjing',
    'cat': 'kucing'
}

# =========================
# VIDEO TRANSFORMER
# =========================
class VideoTransformer(VideoTransformerBase):

    def __init__(self):
        self.last_speech_time = 0
        self.last_objects = set()
        self.cooldown = 5  # detik

    def transform(self, frame):

        img = frame.to_ndarray(format="bgr24")
        img = cv2.flip(img, 1)

        h, w, _ = img.shape

        # =========================
        # OPTIMASI YOLO
        # =========================
        results = model.predict(
            img,
            conf=0.4,
            imgsz=640,
            verbose=False
        )

        detected_now = []

        for r in results:
            for box in r.boxes:

                cls = int(box.cls[0])
                label_en = model.names[cls]

                if label_en not in class_names:
                    continue

                label_id = class_names[label_en]

                x1, y1, x2, y2 = map(int, box.xyxy[0])

                # =========================
                # POSISI OBJEK
                # =========================
                center = (x1 + x2) / 2

                if center < w / 3:
                    posisi = "di kiri"
                elif center < 2 * w / 3:
                    posisi = "di tengah"
                else:
                    posisi = "di kanan"

                label_full = f"{label_id} {posisi}"
                detected_now.append(label_full)

                # DRAW
                cv2.rectangle(img, (x1, y1), (x2, y2), (0,255,0), 2)
                cv2.putText(
                    img,
                    label_full,
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0,255,0),
                    2
                )

        # =========================
        # LOGIC SUARA CERDAS
        # =========================
        now = time.time()
        current_set = set(detected_now)

        if current_set:
            changed = current_set != self.last_objects

            if changed or (now - self.last_speech_time > self.cooldown):

                kalimat = "Saya melihat " + ", ".join(current_set)
                speak(kalimat)

                self.last_speech_time = now
                self.last_objects = current_set

        return img

# =========================
# MAIN APP
# =========================
def run_assistant():

    st.set_page_config(
        page_title="Asisten AI Tunanetra",
        page_icon="👓"
    )

    st.title("👓 Asisten Navigasi AI (Realtime)")
    st.write("Deteksi objek realtime + suara otomatis")

    st.success("Gunakan HP dan aktifkan kamera belakang")

    # SPEAK HANYA SEKALI
    if "started" not in st.session_state:
        speak("Asisten aktif. Saya siap membantu Anda.")
        st.session_state.started = True

    webrtc_streamer(
        key="camera",
        video_transformer_factory=VideoTransformer,
        media_stream_constraints={
            "video": {"facingMode": "environment"},
            "audio": False,
        },
        async_transform=True
    )

# =========================
# RUN
# =========================
if __name__ == "__main__":
    run_assistant()