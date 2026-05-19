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

# --- ३. JAVASCRIPT DIRECT REDIRECTION ENGINE ---
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

# --- ५. REGISTRATION & AUTOMATIC LOGIN TABS ---
if not st.session_state['authenticated']:
    tab1, tab2 = st.tabs(["📝 New User Registration", "🔑 Automatic Biometric Login"])
    
    with tab1:
        st.subheader("नवीन युझर खाते तयार करा")
        reg_name = st.text_input("तुमचे नाव टाका (Enter Your Name):").strip()
        reg_cam = st.camera_input("नोंदणीसाठी एक सरळ चेहरा असलेला फोटो काढा", key="reg_camera")
        
        if st.button("Register Face Now", use_container_width=True):
            if reg_name and reg_cam:
                reg_image = Image.open(reg_cam).convert('RGB')
                st.session_state['user_db'][reg_name] = reg_image
                st.success(f"🎉 {reg_name} ची बायोमेट्रिक नोंदणी यशस्वी झाली आहे! आता लॉगिन टॅबमध्ये जा.")
            else:
                st.error("❌ कृपया नाव आणि फोटो दोन्ही गोष्टी पूर्ण करा.")

    with tab2:
        st.subheader("फक्त कॅमेरा समोर या - सिस्टीम स्वतः ओळखेल")
        
        if len(st.session_state['user_db']) == 0:
            st.warning("⚠️ आधी रजिस्ट्रेशन टॅबमध्ये जाऊन किमान एका युझरची नोंदणी करा.")
        else:
            login_cam = st.camera_input("लॉगिनसाठी चेहऱ्याचा फोटो काढा", key="login_camera")
            
            # 🚀 ऑटोमॅटिक फेस रेकग्निशन (नाव निवडायची गरज नाही!)
            if login_cam:
                with st.spinner("🔄 Scanning Face Database..."):
                    try:
                        login_img = Image.open(login_cam).convert('RGB')
                        login_resized = login_img.resize((300, 300))
                        
                        match_found = False
                        identified_user = None
                        best_score = 1.0
                        
                        # डेटाबेसमधील प्रत्येक रजिस्टर चेहऱ्यासोबत मॅचिंग चेक करणे
                        for name, base_img in st.session_state['user_db'].items():
                            base_resized = base_img.resize((300, 300))
                            
                            diff = ImageChops.difference(base_resized, login_resized)
                            stat = ImageStat.Stat(diff)
                            diff_ratio = sum(stat.mean) / (3 * 255)
                            
                            if diff_ratio < diff_ratio < best_score:
                                best_score = diff_ratio
                                if diff_ratio < 0.35: # थ्रेशोल्ड मॅच
                                    match_found = True
                                    identified_user = name
                        
                        if match_found:
                            st.session_state['authenticated'] = True
                            st.session_state['current_user'] = identified_user
                            st.success(f"🔓 स्वागत आहे {identified_user}! चेहरा ओळखला गेला आहे.")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error("❌ चेहरा ओळखता आला नाही! कृपया पुन्हा प्रयत्न करा.")
                    except Exception as e:
                        st.error(f"प्रमाणीकरण एरर: {e}")

# 🔓 PHASE 2: AUTOMATION CONTROL PANEL (100% HANDS-FREE VOICE)
else:
    st.success(f"🔓 Authenticated Successfully as {st.session_state['current_user']}!")
    
    # लपवलेला रिकामा बॉक्स पूर्णपणे अदृश्य करण्यासाठी CSS
    st.markdown(
        """
        <style>
        div[data-testid="stTextInput"] {
            display: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    if 'hidden_voice_query' not in st.session_state:
        st.session_state['hidden_voice_query'] = ""

    # --- 🎙️ PURE JAVASCRIPT BACKGROUND LIVE STT ENGINE ---
    js_speech_engine = """
    <script>
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            console.log("Web Speech API not supported.");
        } else {
            const recognition = new SpeechRecognition();
            recognition.continuous = true;
            recognition.interimResults = false;
            recognition.lang = 'en-US';

            recognition.onresult = function(event) {
                const current = event.resultIndex;
                const transcript = event.results[current][0].transcript;
                
                window.parent.postMessage({
                    type: 'streamlit:set_widget_value',
                    from: 'js_voice_bridge',
                    value: transcript
                }, '*');
            };

            recognition.onend = function() {
                recognition.start();
            };

            recognition.start();
        }
    </script>
    """
    components.html(js_speech_engine, height=0, width=0)
    
    # व्हॉईस डेटा ब्रिज
    heard_text = st.text_input("", key="js_voice_bridge", label_visibility="collapsed")
    
    # व्हॉईस लॉजिक ओव्हरलॅपिंग आणि लूप फिक्स
    if heard_text and heard_text != st.session_state['hidden_voice_query']:
        st.session_state['hidden_voice_query'] = heard_text
        query = heard_text.lower().strip()
        
        if "python" in query or "paithen" in query or "py" in query:
            st.session_state['last_command'] = query

    st.info(f"💾 **Last Detected Live Voice Command:** {st.session_state['last_command']}")
    st.markdown("🌐 **Status:** `माईक ऑन आहे. थेट बोला (उदा: 'Python open youtube')`")

    # --- ⚡ COMMAND EXECUTION ENGINE (FIXED NO-LOOP) ---
    cmd = st.session_state['last_command']
    if cmd != "None":
        clean_command = cmd.replace("python", "").replace("paithen", "").replace("py", "").strip()
        st.session_state['last_command'] = "None" # एक्झिक्युशन आधीच क्लियर करून लूप तोडणे
        
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
        st.session_state['hidden_voice_query'] = ""
        st.rerun()