# --- SYSTEM OVERRIDE FOR LINUX DRIVERS ---
import sys
import mock
sys.modules['cv2'] = mock.MagicMock()
# -----------------------------------------

import streamlit as st
import numpy as np
from deepface import DeepFace
import io
import os
import time
import webbrowser
import requests

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
        reg_cam = st.camera_input("नोंदणीसाठी एक सरळ चेहरा असलेला फोटो काढा", key="reg_camera")
        
        if st.button("Register Face Now", use_container_width=True):
            if reg_name and reg_cam:
                file_path = f"{reg_name}_base.jpg"
                with open(file_path, "wb") as f:
                    f.write(reg_cam.getbuffer())
                
                st.session_state['user_db'][reg_name] = file_path
                st.success(f"🎉 {reg_name} ची बायोमेट्रिक नोंदणी यशस्वी झाली आहे! अबी भाऊ, आता लॉगिन टॅबमध्ये जा.")
            else:
                st.error("❌ कृपया नाव आणि फोटो दोन्ही गोष्टी पूर्ण करा.")

    # 🔑 टॅब २: बायोमेट्रिक लॉगिन
    with tab2:
        st.subheader("चेहरा दाखवून सिस्टीम अनलॉक करा")
        
        if len(st.session_state['user_db']) == 0:
            st.warning("⚠️ आधी रजिस्ट्रेशन टॅबमध्ये जाऊन किमान एका युझरची नोंदणी करा.")
        else:
            login_name = st.selectbox("तुमचे नाव निवडा (Select Your Name)", list(st.session_state['user_db'].keys()))
            login_cam = st.camera_input("लॉगिनसाठी चेहऱ्याचा फ्रेश फोटो काढा", key="login_camera")
            
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
    st.write("मोबाईलवर वापरताना माईल परमिशन **Allow** करा, बोला आणि स्टॉप करा.")
    
    # 🛠️ मोबाईल माईक फिक्स: आपण फिक्स पॅरामीटर्ससह स्पीच रेकॉर्डर लोड केला आहे
    from streamlit_mic_recorder import speech_to_text
    
    text_received = speech_to_text(
        start_prompt="🎙️ Start Speaking Command (बोलणे सुरू करा)",
        stop_prompt="🛑 Stop & Process (कमांड रन करा)",
        language='en-US', 
        key='web_voice_core_fixed',
        use_container_width=True
    )
    
    if text_received:
        query = text_received.lower().strip()
        st.write(f"🗣️ **सिस्टीमने ऐकलेला शब्द:** `{query}`")
        
        if "python" in query or "paithen" in query or "py" in query:
            clean_command = query.replace("python", "").replace("paithen", "").replace("py", "").strip()
            st.session_state['last_command'] = clean_command
            
            st.success(f"⚙️ Action Triggered: `{clean_command}`")
            
            # --- 📚 १. विकिपीडिया सर्च मॅजिक्स (Special Feature) ---
            if 'wikipedia' in clean_command or 'wiki' in clean_command or 'tell me about' in clean_command:
                # सर्च क्युरी स्वच्छ करणे
                search_term = clean_command.replace("wikipedia", "").replace("wiki", "").replace("tell me about", "").strip()
                st.info(f"🔍 Searching Wikipedia for: `{search_term}`...")
                
                try:
                    wiki_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{search_term.replace(' ', '_')}"
                    response = requests.get(wiki_url, headers={"User-Agent": "UniversalAIBot/1.0"}).json()
                    
                    if "extract" in response:
                        st.markdown(f"### 📖 Wikipedia Summary for **{search_term.title()}**:")
                        st.info(response['extract'])
                    else:
                        st.warning("❌ विकिपीडियावर या विषयाची सोपी माहिती सापडली नाही. गुगल सर्च उघडत आहे...")
                        webbrowser.open(f"https://www.google.com/search?q={search_term}")
                except Exception as wiki_err:
                    st.error(f"विकिपीडिया एरर: {wiki_err}")
            
            # --- 🚀 २. युनिव्हर्सल अ‍ॅप्स ओपनिंग मॅजिक्स ---
            elif 'open' in clean_command or 'start' in clean_command:
                app = clean_command.replace("open ", "").replace("start ", "").strip()
                
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
                elif 'github' in app:
                    webbrowser.open("https://github.com")
                    st.info("Opening GitHub...")
                elif 'chatgpt' in app or 'gpt' in app:
                    webbrowser.open("https://chat.openai.com")
                    st.info("Opening ChatGPT...")
                else:
                    webbrowser.open(f"https://www.google.com/search?q={app}")
                    st.success(f"Searching for '{app}' on Google...")
            else:
                # जर ओपन किंवा विकी नसेल, तर डायरेक्ट गुगल सर्च मारेल
                webbrowser.open(f"https://www.google.com/search?q={clean_command}")
                st.success(f"Searching for '{clean_command}' on Google...")
        else:
            st.warning("⚠️ कमांडमध्ये 'Python' कीवर्ड सापडला नाही. (उदा. बोला: 'Python open youtube')")

    st.write("---")
    if st.button("🛑 Lock System Manually", use_container_width=True):
        st.session_state['authenticated'] = False
        st.session_state['current_user'] = None
        st.rerun()