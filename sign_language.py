import streamlit as st
import cv2
import mediapipe as mp
import pyttsx3
import time

# =========================
# TEXT TO SPEECH
# =========================
engine = pyttsx3.init()

def stop_speech():
    try:
        engine.stop()
    except:
        pass

def speak(text):
    stop_speech()      # hentikan suara sebelumnya
    engine.say(text)
    engine.runAndWait()
# =========================
# CEK JARI
# =========================
def finger_up(hand_landmarks, tip, pip):
    return hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y

# =========================
# APP
# =========================
def run_sign():

    # 🎨 STYLE
    st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #0f172a, #1e293b);
        color: white;
    }
    .title {
        font-size: 40px;
        font-weight: bold;
        text-align: center;
        color: #38bdf8;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<p class="title">🤟 Sign Language AI</p>', unsafe_allow_html=True)

    # =========================
    # SIDEBAR
    # =========================
    st.sidebar.title("⚙️ Pengaturan")

    mode = st.sidebar.selectbox("Mode", ["BISINDO", "SIBI"])
    font_size = st.sidebar.slider("Ukuran Font", 20, 80, 40)
    speak_toggle = st.sidebar.checkbox("Aktifkan Suara", True)
    cooldown = st.sidebar.slider("Delay Suara", 1, 5, 2)

    # =========================
    # CAMERA CONTROL
    # =========================
    run = st.checkbox("Aktifkan Kamera", value=True)

    frame_window = st.empty()
    text_display = st.empty()

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    )

    mp_draw = mp.solutions.drawing_utils

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        st.error("❌ Kamera gagal dibuka")
        return

    last_text = ""
    last_time = 0

    gesture_buffer = []
    buffer_size = 5

    # =========================
    # LOOP
    # =========================
    while run:

        ret, frame = camera.read()

        if not ret:
            st.error("❌ Kamera tidak terdeteksi")
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        text = "Tidak ada gesture"

        if result.multi_hand_landmarks:

            total_hands = len(result.multi_hand_landmarks)

            left_hand = None
            right_hand = None

            for idx, hand_landmarks in enumerate(result.multi_hand_landmarks):

                mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS
                )

                handedness = result.multi_handedness[idx].classification[0].label

                if handedness == "Left":
                    left_hand = hand_landmarks
                else:
                    right_hand = hand_landmarks

            # =========================
            # BISINDO
            # =========================
            if mode == "BISINDO":

                if total_hands == 2 and left_hand and right_hand:
                    if finger_up(left_hand, 8, 6) and finger_up(right_hand, 8, 6):
                        text = "Halo"

                elif total_hands == 1:
                    hand = result.multi_hand_landmarks[0]

                    thumb = finger_up(hand, 4, 2)
                    index = finger_up(hand, 8, 6)
                    middle = finger_up(hand, 12, 10)
                    ring = finger_up(hand, 16, 14)
                    pinky = finger_up(hand, 20, 18)

                    if index and middle and not ring and not pinky:
                        text = "Halo"
                    elif thumb and index and middle and ring and pinky:
                        text = "Terima Kasih"
                    elif index and not middle:
                        text = "Saya"
                    elif pinky and not index:
                        text = "Kamu"
                    elif thumb and index and not middle:
                        text = "Makan"
                    elif thumb and pinky:
                        text = "Minum"
                    elif thumb and index and pinky:
                        text = "I Love You"

            # =========================
            # SIBI
            # =========================
            elif mode == "SIBI":

                if total_hands == 1:
                    hand = result.multi_hand_landmarks[0]

                    thumb = finger_up(hand, 4, 2)
                    index = finger_up(hand, 8, 6)
                    middle = finger_up(hand, 12, 10)
                    ring = finger_up(hand, 16, 14)
                    pinky = finger_up(hand, 20, 18)

                    if index and middle and ring and pinky:
                        text = "Huruf B"
                    elif thumb and index:
                        text = "Huruf C"
                    elif pinky:
                        text = "Huruf I"

        # =========================
        # STABILITY FILTER
        # =========================
        gesture_buffer.append(text)
        if len(gesture_buffer) > buffer_size:
            gesture_buffer.pop(0)

        final_text = max(set(gesture_buffer), key=gesture_buffer.count)

        # =========================
        # TAMPILKAN TEXT (MODERN)
        # =========================
        text_display.markdown(
            f"<h1 style='text-align:center; font-size:{font_size}px; color:#22c55e;'>"
            f"{final_text}</h1>",
            unsafe_allow_html=True
        )

        frame_window.image(frame, channels="BGR")

        # =========================
        # SPEAK
        # =========================
        current_time = time.time()

        if (
            speak_toggle
            and final_text != "Tidak ada gesture"
            and final_text != last_text
            and current_time - last_time > cooldown
        ):
            speak(final_text)
            last_text = final_text
            last_time = current_time

    stop_speech()      # hentikan suara
    camera.release()


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    run_sign()

    ###ini scene 4 Bagiian development 