import streamlit as st
import numpy as np
from deepface import DeepFace
import io
import os
import time
import webbrowser
import requests
from PIL import Image

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
                # PIL Image ऑब्जेक्ट बनवून सेशन स्टेटमध्ये थेट सेव्ह करणे (इमेज लॉस होणार नाही)
                reg_image = Image.open(reg_cam)
                st.session_state['user_db'][reg_name] = reg_image
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
            login_cam = st.camera_input("लॉगिनसाठी चेहऱ्याचा फ्रेश फोटो काढा", key="login_camera")
            
            if login_cam and login_name:
                st.info("🔄 Biometric Facenet Analysis in progress...")
                
                try:
                    # १. बेस फोटो आणि फ्रेश फोटो PIL फॉरमॅटमध्ये मिळवणे
                    base_pil = st.session_state['user_db'][login_name]
                    login_pil = Image.open(login_cam)
                    
                    # २. त्यांना numpy array मध्ये कन्वर्शन करणे (OpenCV ची गरजच नाही)
                    img1 = np.array(base_pil)
                    img2 = np.array(login_pil)
                    
                    # ३. डीपफेस व्हेरिफिकेशन (थेट नंपाय अरे पास करणे)
                    result = DeepFace.verify(img1_path = img1, 
                                             img2_path = img2,
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
    st.write("मोबाईलवर वापरताना माईल परमिशन Allow करा, बोला आणि स्टॉप करा.")
    
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
            
            # --- विकिपीडिया सर्च ---
            if 'wikipedia' in clean_command or 'wiki' in clean_command or 'tell me about' in clean_command:
                search_term = clean_command.replace("wikipedia", "").replace("wiki", "").replace("tell me about", "").strip()
                st.info(f"🔍 Searching Wikipedia for: `{search_term}`...")
                
                try:
                    wiki_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{search_term.replace(' ', '_')}"
                    response = requests.get(wiki_url, headers={"User-Agent": "UniversalAIBot/1.0"}).json()
                    
                    if "extract" in response:
                        st.markdown(f"### 📖 Wikipedia Summary for **{search_term.title()}**:")
                        st.info(response['extract'])
                    else:
                        st.warning("❌ विकिपीडियावर माहिती सापडली नाही. गुगल सर्च उघडत आहे...")
                        webbrowser.open(f"https://www.google.com/search?q={search_term}")
                except Exception as wiki_err:
                    st.error(f"विकिपीडिया एरर: {wiki_err}")
            
            # --- युनिव्हर्सल अ‍ॅप्स ओपनिंग मॅजिक्स ---
            elif 'open' in clean_command or 'start' in clean_command:
                app = clean_command.replace("open ", "").replace("start ", "").strip()
                
                if 'instagram' in app or 'insta' in app:
                    webbrowser.open("https://www.instagram.com")
                    st.info("Opening Instagram...")
                elif 'youtube' in app or 'yt' in app:
                    webbrowser.open("https://www.youtube.com")
                    st.info("Opening YouTube...")
                elif 'google' in app:
                    webbrowser.open("https://www.google.com")
                    st.info("Opening Google...")
                else:
                    webbrowser.open(f"https://www.google.com/search?q={app}")
                    st.success(f"Searching for '{app}' on Google...")
            else:
                webbrowser.open(f"https://www.google.com/search?q={clean_command}")
                st.success(f"Searching for '{clean_command}' on Google...")
        else:
            st.warning("⚠️ कमांडमध्ये 'Python' कीवर्ड सापडला नाही.")

    st.write("---")
    if st.button("🛑 Lock System Manually", use_container_width=True):
        st.session_state['authenticated'] = False
        st.session_state['current_user'] = None
        st.rerun()