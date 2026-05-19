import streamlit as st
import cv2
from deepface import DeepFace
import speech_recognition as sr
import pyttsx3
import pyautogui
import time
import subprocess
import os

# --- १. STREAMLIT PAGE SET-UP & THEME ---
st.set_page_config(
    page_title="Abhijeet's AI Hub",
    page_icon="🤖",
    layout="centered"
)

# कस्टमाइज्ड CSS - प्रिमियम लुक
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button {
        background-color: #4A90E2;
        color: white;
        font-size: 18px;
        font-weight: bold;
        border-radius: 8px;
        padding: 10px 24px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #357ABD;
        transform: scale(1.02);
    }
    .auth-box {
        padding: 20px;
        border-radius: 10px;
        border: 2px dashed #4A90E2;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 Next-Gen Voice & Face Automation Bot")
st.write("---")

# --- २. SESSION STATE VARIABLES ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'last_command' not in st.session_state:
    st.session_state['last_command'] = "None"
if 'bot_status' not in st.session_state:
    st.session_state['bot_status'] = "Idle"
if 'start_cam' not in st.session_state:
    st.session_state['start_cam'] = False

# --- ३. सुरक्षित व्हॉइ‍स इंजिन सेटअप ---
if 'voice_engine' not in st.session_state:
    try:
        st.session_state['voice_engine'] = pyttsx3.init('sapi5')
        voices = st.session_state['voice_engine'].getProperty('voices')
        st.session_state['voice_engine'].setProperty('voice', voices[0].id)
        st.session_state['voice_engine'].setProperty('rate', 180)
    except Exception as e:
        print(f"Voice Init Error: {e}")

def speak(audio):
    st.session_state['bot_status'] = f"Speaking: {audio}"
    try:
        if 'voice_engine' in st.session_state:
            engine = st.session_state['voice_engine']
            engine.say(audio)
            engine.runAndWait()
    except RuntimeError:
        time.sleep(0.5)

# --- ४. VOICE RECOGNITION FUNCTION ---
def take_command():
    r = sr.Recognizer()
    r.energy_threshold = 300  
    r.dynamic_energy_threshold = True
    
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.5)
        try:
            st.session_state['bot_status'] = "🎤 Listening for 'Python + Command'..."
            audio = r.listen(source, timeout=3, phrase_time_limit=4)
            st.session_state['bot_status'] = "🧠 Processing voice waves..."
            query = r.recognize_google(audio, language='en-in').lower()
            
            if "python" in query:
                clean_command = query.replace("python", "").strip()
                st.session_state['last_command'] = clean_command
                return clean_command
            return "none"
        except Exception:
            return "none"

# --- ५. MAIN WEB UI RENDERING ---
col1, col2 = st.columns(2)
with col1:
    st.metric(label="🔐 Security Status", value="UNLOCKED" if st.session_state['authenticated'] else "LOCKED")
with col2:
    st.metric(label="🔄 Bot Mode", value=st.session_state['bot_status'])

st.write("---")

# 🔒 PHASE 1: BIOMETRIC LOGIN WITH INDEX 3 FIXED
if not st.session_state['authenticated']:
    st.markdown("<div class='auth-box'><h3>⚠️ Biometric Lock Enabled</h3><p>प्रणालीचा वापर करण्यासाठी आधी चेहरा प्रमाणीकरण करणे बंधनकारक आहे.</p></div>", unsafe_allow_html=True)
    st.write("")
    
    if not st.session_state['start_cam']:
        if st.button("🔒 Trigger Mobile Face Scanner (Index 3)", use_container_width=True):
            st.session_state['start_cam'] = True
            st.rerun()
    else:
        # व्हेरिफाय आणि कॅन्सल बटन्स
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            verify_click = st.button("📸 Capture & Verify Now", use_container_width=True)
        with col_btn2:
            if st.button("🛑 Stop Scanner", use_container_width=True):
                st.session_state['start_cam'] = False
                st.rerun()

        # कॅमेरा फीडसाठी स्क्रीनवर जागा
        frame_placeholder = st.empty()
        
        # 🎥 थेट कॅमेरा इंडेक्स ३ ला ओपन करणे
        # cap = cv2.VideoCapture(3, cv2.CAP_DSHOW)
        # ✅ आपल्या मुख्य कोडमध्ये ही ओळ परफेक्ट करून घ्या:
        cap = cv2.VideoCapture(3, cv2.CAP_DSHOW)
        
        # कॅमेरा वॉर्मअप आणि जुना बफर पूर्ण साफ करण्यासाठी ओळी
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        time.sleep(1.0)
        
        # लाईव्ह फीड लूप
        while cap.isOpened() and not verify_click:
            ret, frame = cap.read()
            if not ret or frame is None:
                st.error("Index 3 वरून मोबाईल कॅमेरा फीड मिळत नाहीये. Iriun ॲप चालू असल्याची खात्री करा.")
                break
                
            # स्क्रीनवर लाईव्ह दाखवण्यासाठी RGB कन्व्हर्ट
            preview_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_placeholder.image(preview_frame, channels="RGB", caption="LIVE FEED FROM INDEX 3 - Look at your mobile camera")
            
            # हा छोटा स्लीप लूपला अडकण्यापासून वाचवतो
            time.sleep(0.01)
            
            # जर युझरने बटणावर क्लिक केलं तर लूप ताबडतोब ब्रेक होईल
            if verify_click:
                break
        
        # क्लिक झाल्यावर ताजी फ्रेम पकडणे
        if verify_click:
            # जुन्या साठलेल्या फ्रेम्स साफ करण्यासाठी सलग ३ फ्रेम्स वाचून टाकणे (बफर फिक्स)
            for _ in range(3):
                cap.read()
                
            ret, final_frame = cap.read()
            if ret and final_frame is not None:
                cv2.imwrite("verify.jpg", final_frame)
                cap.release()
                frame_placeholder.empty()
                
                st.info("🔄 Biometric Analysis in progress...")
                try:
                    result = DeepFace.verify(img1_path = "abhijeet.jpg", 
                                             img2_path = "verify.jpg",
                                             model_name = "VGG-Face",
                                             distance_metric = "cosine", 
                                             enforce_detection = False)
                    
                    dist = result['distance']
                    
                    if dist < 0.50: 
                        st.session_state['authenticated'] = True
                        st.session_state['start_cam'] = False
                        st.session_state['bot_status'] = "System Unlocked"
                        speak("Access Granted! Welcome Abhijeet.")
                        st.rerun()
                    else:
                        speak("Access Denied! Face mismatch.")
                        st.error(f"Authentication Failed! Distance Score: {round(dist, 2)}")
                        st.session_state['start_cam'] = False
                        st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
                    speak("Verification error. Please retry.")
                    st.session_state['start_cam'] = False
                    st.rerun()
            cap.release()

# 🔓 PHASE 2: SYSTEM PANEL
else:
    st.success("🔓 Authenticated Successfully as Abhijeet Thombare!")
    st.info(f"💾 **Last Detected Command:** {st.session_state['last_command']}")
    
    if st.button("🎙️ Wake Up Voice Core (Listen 1 Command)", use_container_width=True):
        query = take_command()
        
        if query != "none" and query != "":
            st.write(f"⚙️ **Executing System Action:** `{query}`")
            
            if 'home page' in query or 'desktop' in query:
                pyautogui.hotkey('win', 'd')
                speak("Showing your desktop.")
            elif 'screenshot' in query:
                pyautogui.screenshot(f"ss_{int(time.time())}.png")
                speak("Screenshot successfully saved.")
            elif 'open' in query or 'start' in query:
                app = query.replace("open ", "").replace("start ", "").strip()
                speak(f"Opening {app}")
                if 'chrome' in app or 'browser' in app:
                    subprocess.Popen(["C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"])
                elif 'notepad' in app:
                    subprocess.Popen(["notepad.exe"])
                elif 'calculator' in app or 'calc' in app:
                    subprocess.Popen(["calc.exe"])
                elif 'cmd' in app or 'command prompt' in app:
                    subprocess.Popen(["cmd.exe"])
                else:
                    pyautogui.press('win')
                    time.sleep(0.8) 
                    pyautogui.write(app)
                    time.sleep(0.5)
                    pyautogui.press('enter')
            elif 'lock' in query or 'logout' in query:
                st.session_state['authenticated'] = False
                speak("Locking session. Goodbye!")
                st.rerun()
        else:
            st.session_state['bot_status'] = "Idle"
            st.warning("आवाज स्पष्ट आला नाही किंवा तुम्ही 'Python' कीवर्ड वापरला नाही.")

    if st.button("🛑 Lock System Manually", type="secondary"):
        st.session_state['authenticated'] = False
        st.session_state['bot_status'] = "Idle"
        st.rerun()