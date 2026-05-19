import streamlit as st
import numpy as np
import io
import os
import time
import webbrowser
import requests
from PIL import Image, ImageChops, ImageStat

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
                reg_image = Image.open(reg_cam).convert('RGB')
                st.session_state['user_db'][reg_name] = reg_image
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
                st.info("🔄 Biometric Analysis in progress...")
                
                try:
                    base_img = st.session_state['user_db'][login_name]
                    login_img = Image.open(login_cam).convert('RGB')
                    
                    base_resized = base_img.resize((300, 300))
                    login_resized = login_img.resize((300, 300))
                    
                    diff = ImageChops.difference(base_resized, login_resized)
                    stat = ImageStat.Stat(diff)
                    diff_ratio = sum(stat.mean) / (3 * 255)
                    
                    if diff_ratio < 0.35:
                        st.session_state['authenticated'] = True
                        st.session_state['current_user'] = login_name
                        st.success(f"🔓 स्वागत आहे {login_name}! सिस्टीम अनलॉक झाली.")
                        time.sleep(1.0)
                        st.rerun()
                    else:
                        st.error(f"❌ चेहरा मॅच झाला नाही! (Distance Score: {round(diff_ratio, 2)})")
                except Exception as e:
                    st.error(f"प्रमाणीकरण एरर: {e}")

# 🔓 PHASE 2: AUTOMATION CONTROL PANEL (UNIVERSAL APP COMMANDS)
else:
    st.success(f"🔓 Authenticated Successfully as {st.session_state['current_user']}!")
    st.info(f"💾 **Last Detected Command:** {st.session_state['last_command']}")
    
    st.markdown("### 🎙️ Web Voice Automation Command Center")
    st.write("मोबाईलवर वापरताना माईल परमिशन **Allow** करा, बोला आणि स्टॉप करा.")
    
    from streamlit_mic_recorder import speech_to_text
    
    text_received = speech_to_text(
        start_prompt="🎙️ Start Speaking Command",
        stop_prompt="🛑 Stop & Process",
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
            
            # --- 📚 १. विकिपीडिया सर्च ---
            if 'wikipedia' in clean_command or 'wiki' in clean_command or 'tell me about' in clean_command:
                search_term = clean_command.replace("wikipedia", "").replace("wiki", "").replace("tell me about", "").strip()
                try:
                    wiki_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{search_term.replace(' ', '_')}"
                    response = requests.get(wiki_url, headers={"User-Agent": "UniversalAIBot/1.0"}).json()
                    if "extract" in response:
                        st.markdown(f"### 📖 Wikipedia Summary:")
                        st.info(response['extract'])
                    else:
                        webbrowser.open(f"https://www.google.com/search?q={search_term}")
                except Exception as wiki_err:
                    st.error(f"विकिपीडिया एरर: {wiki_err}")
            
            # --- 📱 २. अल्टीमेट मोबाईल हार्डवेअर आणि सेटिंग्स ऑटोमेशन (Android/iOS Special) ---
            elif any(x in clean_command for x in ['wifi', 'wi-fi', 'data', 'internet', 'torch', 'flashlight', 'bluetooth', 'hotspot', 'location', 'gps', 'settings']):
                st.info("🔄 Triggering Mobile Hardware System Intent...")
                
                # Wi-Fi Settings उघडण्यासाठी
                if 'wifi' in clean_command or 'wi-fi' in clean_command:
                    webbrowser.open("intent:#Intent;action=android.settings.WIFI_SETTINGS;end") # Android
                    webbrowser.open("App-Prefs:root=WIFI") # iOS Backup
                    st.success("Opening Wi-Fi Settings Panel...")
                
                # Mobile Data / Cellular Settings उघडण्यासाठी
                elif 'data' in clean_command or 'internet' in clean_command:
                    webbrowser.open("intent:#Intent;action=android.settings.DATA_ROAMING_SETTINGS;end")
                    webbrowser.open("App-Prefs:root=MOBILE_DATA_SETTINGS_ID")
                    st.success("Opening Mobile Data Settings...")
                
                # Location / GPS Settings उघडण्यासाठी
                elif 'location' in clean_command or 'gps' in clean_command:
                    webbrowser.open("intent:#Intent;action=android.settings.LOCATION_SOURCE_SETTINGS;end")
                    webbrowser.open("App-Prefs:root=Privacy&path=LOCATION")
                    st.success("Opening Location (GPS) Settings...")

                # Hotspot / Tethering Settings उघडण्यासाठी
                elif 'hotspot' in clean_command or 'tethering' in clean_command:
                    webbrowser.open("intent:#Intent;action=android.settings.TETHER_SETTINGS;end")
                    webbrowser.open("App-Prefs:root=INTERNET_TETHERING")
                    st.success("Opening Hotspot Settings...")

                # Bluetooth Settings उघडण्यासाठी
                elif 'bluetooth' in clean_command:
                    webbrowser.open("intent:#Intent;action=android.settings.BLUETOOTH_SETTINGS;end")
                    webbrowser.open("App-Prefs:root=Bluetooth")
                    st.success("Opening Bluetooth Settings...")

                # Torch / Flashlight (मोबाईलमध्ये टॉर्च टॉगल करण्यासाठी थेट सिस्टीम अ‍ॅक्सेस)
                elif 'torch' in clean_command or 'flashlight' in clean_command:
                    webbrowser.open("intent:#Intent;action=android.media.action.STILL_IMAGE_CAMERA;end") # कॅमेरा फ्लॅश डायरेक्ट ट्रिगर
                    st.success("Opening Camera Hardware Interface for Torch/Flashlight Access...")

            # --- 🚀 ३. युनिव्हर्सल मोबाईल अ‍ॅप्स ओपनिंग मॅजिक्स (Deep Linking) ---
            elif 'open' in clean_command or 'start' in clean_command:
                app = clean_command.replace("open ", "").replace("start ", "").strip()
                
                if 'instagram' in app or 'insta' in app:
                    webbrowser.open("instagram://app")
                    st.info("Opening Instagram App...")
                elif 'youtube' in app or 'yt' in app:
                    webbrowser.open("youtube://")
                    st.info("Opening YouTube App...")
                elif 'whatsapp' in app:
                    webbrowser.open("whatsapp://send")
                    st.info("Opening WhatsApp App...")
                elif 'facebook' in app or 'fb' in app:
                    webbrowser.open("fb://")
                    st.info("Opening Facebook App...")
                elif 'maps' in app or 'map' in app:
                    webbrowser.open("geo:0,0?q=maps") # मोबाईल गुगल मॅप्स डायरेक्ट अ‍ॅप उघडेल
                    st.info("Opening Google Maps App...")
                elif 'gmail' in app or 'mail' in app:
                    webbrowser.open("googlegmail://")
                    st.info("Opening Gmail App...")
                elif 'github' in app:
                    webbrowser.open("https://github.com")
                    st.info("Opening GitHub...")
                else:
                    webbrowser.open(f"https://www.google.com/search?q={app}")
                    st.success(f"Searching for '{app}' on Google...")
            else:
                webbrowser.open(f"https://www.google.com/search?q={clean_command}")

    st.write("---")
    if st.button("🛑 Lock System Manually", use_container_width=True):
        st.session_state['authenticated'] = False
        st.session_state['current_user'] = None
        st.rerun()