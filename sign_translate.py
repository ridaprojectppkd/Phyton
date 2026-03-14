import streamlit as st
import cv2
import mediapipe as mp

st.title("Penerjemah Bahasa Isyarat ke Teks")
st.write("Arahkan tangan ke kamera")

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

camera = cv2.VideoCapture(0)

run = st.checkbox('Aktifkan Kamera')

frame_window = st.image([])

while run:
    ret, frame = camera.read()
    if not ret:
        st.write("Kamera tidak terdeteksi")
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    result = hands.process(rgb)

    text = "Tidak ada gesture"

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # contoh logika sederhana
            if hand_landmarks.landmark[8].y < hand_landmarks.landmark[6].y:
                text = "Halo"

    cv2.putText(frame, text, (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

    frame_window.image(frame)

camera.release()