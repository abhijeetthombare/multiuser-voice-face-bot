import streamlit as st
import cv2
import numpy as np
from deepface import DeepFace
import speech_recognition as sr
import io
import os
import time
import webbrowser

# --- १. PAGE SET-UP & THEME ---
st.set_page_config(
    page_title="Universal AI Hub",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Next-Gen Multi-User Voice & Face Bot")
st.write("---")

# --- २. MULTI-USER SESSION STATES ---
if 'user_db' not in st.session_state:
    st.session_state['user_db'] = {} 
if 'current_user' not in st.session_state:
    st.session_state['current_user'] = None
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'last_command' not in st.session_state:
    st.session_state['last_command'] = "None"

# --- ३. MAIN UI RENDERING ---
col1, col2 = st.columns(2)
with col1:
    status_text = f"🔓 UNLOCKED ({st.session_state['current_user']})" if st.session_state['authenticated'] else "LOCKED 🔒"
    st.metric(label="🔐 Security Status", value=status_text)
with col2:
    st.metric(label="👥 Registered Users", value=len(st.session_state['user_db']))

st.write("---")

# --- ४. REGISTRATION & LOGIN TABS ---
if not st.session_state['authenticated']:
    tab1, tab2 = st.tabs(["📝 New User Registration", "🔑 Biometric Login"])
    
    # 📝 टॅब १: नवीन युझर रजिस्ट्रेशन
    with tab1:
        st.subheader("नवीन युझर खाते तयार करा")
        reg_name = st.text_input("तुमचे नाव टाका (Enter Your Name):").strip()
        reg_cam = st.camera_input("नोंदणीसाठी एक सरळ चेहरा असलेला फोटो काढा")
        
        if st.button("Register Face Now", use_container_width=True):
            if reg_name and reg_cam:
                file_path = f"{reg_name}_base.jpg"
                with open(file_path, "wb") as f:
                    f.write(reg_cam.getbuffer())
                
                st.session_state['user_db'][reg_name] = file_path
                st.success(f"🎉 {reg_name} ची बायोमेट्रिक नोंदणी यशस्वी झाली आहे! आता लॉगिन टॅबमध्ये जा.")
            else:
                st.error("❌ कृपया नाव आणि फोटो दोन्ही गोष्टी पूर्ण करा.")

    # 🔑 टॅब २: बायोमेट्रिक लॉगिन
    with tab2:
        st.subheader("चेहरा दाखवून सिस्टीम अनलॉक करा")
        
        if len(st.session_state['user_db']) == 0:
            st.warning("⚠️ आधी रजिस्ट्रेशन टॅबमध्ये जाऊन किमान एका युझरची नोंदणी करा.")
        else:
            login_name = st.selectbox("तुमचे नाव निवडा (Select Your Name)", list(st.session_state['user_db'].keys()))
            login_cam = st.camera_input("लॉगिनसाठी चेहऱ्याचा फ्रेश फोटो काढा")
            
            if login_cam and login_name:
                with open("temp_login.jpg", "wb") as f:
                    f.write(login_cam.getbuffer())
                
                st.info("🔄 Biometric Facenet Analysis in progress...")
                
                try:
                    base_img = st.session_state['user_db'][login_name]
                    result = DeepFace.verify(img1_path = base_img, 
                                             img2_path = "temp_login.jpg",
                                             model_name = "Facenet",
                                             distance_metric = "cosine", 
                                             enforce_detection = False)
                    dist = result['distance']
                    
                    if dist < 0.65:
                        st.session_state['authenticated'] = True
                        st.session_state['current_user'] = login_name
                        st.success(f"🔓 स्वागत आहे {login_name}! सिस्टीम अनलॉक झाली.")
                        time.sleep(1.0)
                        st.rerun()
                    else:
                        st.error(f"❌ चेहरा मॅच झाला नाही! (Distance Score: {round(dist, 2)})")
                except Exception as e:
                    st.error(f"प्रमाणीकरण एरर: {e}")

# 🔓 PHASE 2: AUTOMATION CONTROL PANEL (UNIVERSAL APP COMMANDS)
else:
    st.success(f"🔓 Authenticated Successfully as {st.session_state['current_user']}!")
    st.info(f"💾 **Last Detected Command:** {st.session_state['last_command']}")
    
    st.markdown("### 🎙️ Web Voice Automation Command Center")
    st.write("खालील बटनावर क्लिक करा, बोला आणि पुन्हा बटन दाबून स्टॉप करा (उदा. 'Python open instagram')")
    
    from streamlit_mic_recorder import speech_to_text
    
    text_received = speech_to_text(
        start_prompt="🎙️ Start Speaking Command",
        stop_prompt="🛑 Stop & Process",
        language='en-US', 
        key='web_voice_core',
        use_container_width=True
    )
    
    if text_received:
        query = text_received.lower()
        st.write(f"🗣️ **सिस्टीमने ऐकलेला शब्द:** `{query}`")
        print(f"\n[LIVE DEBUG] गुगलने ऐकलेला शब्द: '{query}'\n")
        
        if "python" in query or "paithen" in query or "py" in query:
            clean_command = query.replace("python", "").replace("paithen", "").replace("py", "").strip()
            st.session_state['last_command'] = clean_command
            
            st.success(f"⚙️ Action Triggered: `{clean_command}`")
            
            # --- 🚀 युनिव्हर्सल अ‍ॅप्स ओपनिंग मॅजिक्स (मोबाईल + लॅपटॉप दोन्हीसाठी) ---
            if 'open' in clean_command or 'start' in clean_command:
                app = clean_command.replace("open ", "").replace("start ", "").strip()
                
                # सोशल मीडिया आणि मेसेंजर्स
                if 'instagram' in app or 'insta' in app:
                    webbrowser.open("https://www.instagram.com")
                    st.info("Opening Instagram...")
                elif 'facebook' in app or 'fb' in app:
                    webbrowser.open("https://www.facebook.com")
                    st.info("Opening Facebook...")
                elif 'whatsapp' in app:
                    webbrowser.open("https://web.whatsapp.com")
                    st.info("Opening WhatsApp...")
                elif 'telegram' in app or 'tg' in app:
                    webbrowser.open("https://t.me")
                    st.info("Opening Telegram...")
                elif 'linkedin' in app:
                    webbrowser.open("https://www.linkedin.com")
                    st.info("Opening LinkedIn...")
                
                # गुगल आणि व्हिडिओ टूल्स
                elif 'youtube' in app or 'yt' in app:
                    webbrowser.open("https://www.youtube.com")
                    st.info("Opening YouTube...")
                elif 'google' in app:
                    webbrowser.open("https://www.google.com")
                    st.info("Opening Google...")
                elif 'gmail' in app or 'mail' in app:
                    webbrowser.open("https://mail.google.com")
                    st.info("Opening Gmail...")
                elif 'map' in app or 'maps' in app:
                    webbrowser.open("https://maps.google.com")
                    st.info("Opening Google Maps...")
                
                # कोडिंग आणि एज्युकेशन (MIT MCA स्पेशल)
                elif 'github' in app:
                    webbrowser.open("https://github.com")
                    st.info("Opening GitHub...")
                elif 'chatgpt' in app or 'gpt' in app:
                    webbrowser.open("https://chat.openai.com")
                    st.info("Opening ChatGPT...")
                
                # 🔍 ऑटो-सर्च (स्मार्ट बॅकअप): जर वरील यादीत अ‍ॅप नसेल, तर ते डायरेक्ट गुगलवर सर्च मारेल!
                else:
                    webbrowser.open(f"https://www.google.com/search?q={app}")
                    st.success(f"Searching for '{app}' on Google...")
                    
        else:
            st.warning("⚠️ कमांडमध्ये 'Python' कीवर्ड सापडला नाही.")

    st.write("---")
    if st.button("🛑 Lock System Manually", use_container_width=True):
        st.session_state['authenticated'] = False
        st.session_state['current_user'] = None
        st.rerun()