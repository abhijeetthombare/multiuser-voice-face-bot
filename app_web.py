import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import io
import os
import time
import requests
from PIL import Image, ImageChops, ImageStat

# --- १. PAGE SET-UP & THEME ---
st.set_page_config(
    page_title="Universal AI Hub",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Next-Gen Multi-User Voice & Face Bot (Fully Automatic)")
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
if 'redirect_url' not in st.session_state:
    st.session_state['redirect_url'] = None

# --- ३. JAVASCRIPT DIRECT REDIRECTION ENGINE ---
if st.session_state['redirect_url']:
    js_code = f"""
    <script>
        window.open("{st.session_state['redirect_url']}", "_blank");
    </script>
    """
    components.html(js_code, height=0, width=0)
    st.session_state['redirect_url'] = None

# --- ४. MAIN UI RENDERING ---
col1, col2 = st.columns(2)
with col1:
    status_text = f"🔓 UNLOCKED ({st.session_state['current_user']})" if st.session_state['authenticated'] else "LOCKED 🔒"
    st.metric(label="🔐 Security Status", value=status_text)
with col2:
    st.metric(label="👥 Registered Users", value=len(st.session_state['user_db']))

st.write("---")

# --- ५. REGISTRATION & LOGIN TABS ---
if not st.session_state['authenticated']:
    tab1, tab2 = st.tabs(["📝 New User Registration", "🔑 Biometric Login"])
    
    # 📝 Tab 1: New User Registration
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

    # 🔑 Tab 2: Biometric Login (NO BUTTON CLICK NEEDED)
    with tab2:
        st.subheader("चेहरा दाखवून सिस्टीम अनलॉक करा")
        
        if len(st.session_state['user_db']) == 0:
            st.warning("⚠️ आधी रजिस्ट्रेशन टॅबमध्ये जाऊन किमान एका युझरची नोंदणी करा.")
        else:
            login_name = st.selectbox("तुमचे नाव निवडा (Select Your Name)", list(st.session_state['user_db'].keys()))
            login_cam = st.camera_input("लॉगिनसाठी चेहऱ्याचा फोटो काढा (कॅमेरा समोर या)", key="login_camera")
            
            if login_cam:
                with st.spinner("🔄 Biometric Analysis in progress..."):
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
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error(f"❌ चेहरा मॅच झाला नाही! (Distance Score: {round(diff_ratio, 2)})")
                    except Exception as e:
                        st.error(f"प्रमाणीकरण एरर: {e}")

# 🔓 PHASE 2: AUTOMATION CONTROL PANEL (NO BUTTONS - DIRECT STT LISTENING)
else:
    st.success(f"🔓 Authenticated Successfully as {st.session_state['current_user']}!")
    st.info(f"💾 **Last Detected Command:** {st.session_state['last_command']}")
    
    st.markdown("### 🎙️ Mobile Voice Automation Hub (Auto-Capture Mode)")
    
    # Text input field designed for direct voice-to-text typing from mobile keyboard mic (No buttons needed)
    query_input = st.text_input("🎙️ Voice Active: Mobile maik var click karun fkt bola:", key="auto_voice_trigger")
    
    if query_input:
        query = query_input.lower().strip()
        st.write(f"🗣️ **सिस्टीमने ऐकलेला शब्द:** `{query}`")
        
        if "python" in query or "paithen" in query or "py" in query:
            clean_command = query.replace("python", "").replace("paithen", "").replace("py", "").strip()
            st.session_state['last_command'] = clean_command
            
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
                        st.session_state['redirect_url'] = f"https://www.google.com/search?q={search_term}"
                        st.rerun()
                except Exception as wiki_err:
                    st.error(f"विकिपीडिया एरर: {wiki_err}")
            
            # --- 📱 २. मोबाईल सिस्टीम सेटिंग्ज ---
            elif any(x in clean_command for x in ['wifi', 'wi-fi', 'data', 'internet', 'location', 'gps', 'hotspot', 'tethering', 'bluetooth']):
                if 'wifi' in clean_command or 'wi-fi' in clean_command:
                    st.session_state['redirect_url'] = "intent:#Intent;action=android.settings.WIFI_SETTINGS;end"
                elif 'data' in clean_command or 'internet' in clean_command:
                    st.session_state['redirect_url'] = "intent:#Intent;action=android.settings.DATA_ROAMING_SETTINGS;end"
                elif 'location' in clean_command or 'gps' in clean_command:
                    st.session_state['redirect_url'] = "intent:#Intent;action=android.settings.LOCATION_SOURCE_SETTINGS;end"
                elif 'hotspot' in clean_command or 'tethering' in clean_command:
                    st.session_state['redirect_url'] = "intent:#Intent;action=android.settings.TETHER_SETTINGS;end"
                elif 'bluetooth' in clean_command:
                    st.session_state['redirect_url'] = "intent:#Intent;action=android.settings.BLUETOOTH_SETTINGS;end"
                st.rerun()
            
            # --- 🚀 ३. युनिव्हर्सल मोबाईल ॲप्स ---
            elif 'open' in clean_command or 'start' in clean_command:
                app = clean_command.replace("open ", "").replace("start ", "").strip()
                
                if 'instagram' in app or 'insta' in app:
                    st.session_state['redirect_url'] = "instagram://app"
                elif 'youtube' in app or 'yt' in app:
                    st.session_state['redirect_url'] = "youtube://"
                elif 'whatsapp' in app:
                    st.session_state['redirect_url'] = "whatsapp://send"
                elif 'facebook' in app or 'fb' in app:
                    st.session_state['redirect_url'] = "fb://"
                elif 'maps' in app or 'map' in app:
                    st.session_state['redirect_url'] = "geo:0,0?q=maps"
                elif 'gmail' in app or 'mail' in app:
                    st.session_state['redirect_url'] = "googlegmail://"
                else:
                    st.session_state['redirect_url'] = f"https://www.google.com/search?q={app}"
                st.rerun()
            else:
                st.session_state['redirect_url'] = f"https://www.google.com/search?q={clean_command}"
                st.rerun()

    st.write("---")
    if st.button("🛑 Lock System Manually", use_container_width=True):
        st.session_state['authenticated'] = False
        st.session_state['current_user'] = None
        st.rerun()