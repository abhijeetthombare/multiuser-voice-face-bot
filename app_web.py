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

st.title("🤖 Next-Gen Multi-User Voice & Face Bot (Pure Hands-Free)")
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

# --- ३. JAVASCRIPT AUTOMATION ENGINE (REDIRECTION & CONTINUOUS VOICE) ---
if st.session_state['redirect_url']:
    js_redirect = f"""
    <script>
        window.open("{st.session_state['redirect_url']}", "_blank");
    </script>
    """
    components.html(js_redirect, height=0, width=0)
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

    with tab2:
        st.subheader("चेहरा दाखवून सिस्टीम अनलॉक करा")
        
        if len(st.session_state['user_db']) == 0:
            st.warning("⚠️ आधी रजिस्ट्रेशन टॅबमध्ये जाऊन किमान एका युझरची नोंदणी करा.")
        else:
            login_name = st.selectbox("तुमचे नाव निवडा (Select Your Name)", list(st.session_state['user_db'].keys()))
            login_cam = st.camera_input("लॉगिनसाठी चेहऱ्याचा फोटो काढा (कॅмера समोर या)", key="login_camera")
            
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

# 🔓 PHASE 2: AUTOMATION CONTROL PANEL (100% HANDS-FREE VOICE)
else:
    st.success(f"🔓 Authenticated Successfully as {st.session_state['current_user']}!")
    
    # गुपचूप बॅकएंडला व्हॉईस डेटा प्रोसेस करण्यासाठी लपवलेला इनपुट बॉक्स
    if 'hidden_voice_query' not in st.session_state:
        st.session_state['hidden_voice_query'] = ""

    # --- 🎙️ PURE JAVASCRIPT BACKGROUND LIVE STT ENGINE ---
    # हा कोड ब्राउझरचा माईक ऑन ठेवतो, बटणाची गरजच नाही!
    js_speech_engine = """
    <script>
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            console.log("Web Speech API not supported in this browser.");
        } else {
            const recognition = new SpeechRecognition();
            recognition.continuous = true;
            recognition.interimResults = false;
            recognition.lang = 'en-US';

            recognition.onstart = function() {
                console.log("Voice recognition activated. Listening continuously...");
            };

            recognition.onresult = function(event) {
                const current = event.resultIndex;
                const transcript = event.results[current][0].transcript;
                console.log("Heard: " + transcript);
                
                # स्ट्रीमलिटच्या गुपचूप बॉक्समध्ये डेटा ढकलणे
                window.parent.postMessage({
                    type: 'streamlit:set_widget_value',
                    from: 'js_voice_bridge',
                    value: transcript
                }, '*');
            };

            recognition.onerror = function(event) {
                console.log("Error occurred in recognition: " + event.error);
            };

            // माईक बंद पडला तर ऑटोमॅटिक पुन्हा सुरू करणे (Continuous Loop)
            recognition.onend = function() {
                recognition.start();
            };

            recognition.start();
        }
    </script>
    """
    # JavaScript बॅकएंडला रन करणे
    components.html(js_speech_engine, height=0, width=0)
    
    # हा तो लपवलेला ब्रिज आहे जो JavaScript चा आवाज पायथॉनमध्ये आणतो
    heard_text = st.text_input("🎙️ System Status: Continuous Listening...", key="js_voice_bridge", label_visibility="collapsed")
    
    if heard_text and heard_text != st.session_state['hidden_voice_query']:
        st.session_state['hidden_voice_query'] = heard_text
        query = heard_text.lower().strip()
        st.session_state['last_command'] = query
        st.rerun()

    st.info(f"💾 **Last Detected Live Voice Command:** {st.session_state['last_command']}")
    st.markdown("🌐 **Status:** `माईक ऑटोमॅटिक सुरू आहे. थेट बोला (उदा: 'Python open youtube')`")

    # --- ⚡ COMMAND EXECUTION ENGINE ---
    cmd = st.session_state['last_command']
    if "python" in cmd or "paithen" in cmd or "py" in cmd:
        clean_command = cmd.replace("python", "").replace("paithen", "").replace("py", "").strip()
        st.success(f"⚙️ Running Automatic Action: `{clean_command}`")
        st.session_state['last_command'] = "None" # लूप टाळण्यासाठी रीसेट
        
        # --- १. मोबाईल सिस्टीम सेटिंग्ज ---
        if any(x in clean_command for x in ['wifi', 'wi-fi', 'data', 'internet', 'location', 'gps', 'hotspot', 'tethering', 'bluetooth']):
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
        
        # --- २. युनिव्हर्सल मोबाईल ॲप्स ---
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

    st.write("---")
    if st.button("🛑 Lock System Manually", use_container_width=True):
        st.session_state['authenticated'] = False
        st.session_state['current_user'] = None
        st.session_state['last_command'] = "None"
        st.rerun()