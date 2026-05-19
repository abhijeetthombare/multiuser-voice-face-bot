import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import io
import os
import time
from PIL import Image, ImageChops, ImageStat

# --- १. PAGE SET-UP & THEME ---
st.set_page_config(
    page_title="Universal AI Hub",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Next-Gen Multi-User Voice Bot (Fully Integrated)")
st.write("---")

# --- २. MULTI-USER SESSION STATES ---
if 'user_db' not in st.session_state:
    st.session_state['user_db'] = {} 
if 'current_user' not in st.session_state:
    st.session_state['current_user'] = None
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

# --- ३. MAIN UI RENDERING ---
col1, col2 = st.columns(2)
with col1:
    status_text = f"🔓 UNLOCKED ({st.session_state['current_user']})" if st.session_state['authenticated'] else "LOCKED 🔒"
    st.metric(label="🔐 Security Status", value=status_text)
with col2:
    st.metric(label="👥 Registered Users", value=len(st.session_state['user_db']))

st.write("---")

# --- ४. REGISTRATION & AUTOMATIC LOGIN TABS ---
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
                st.success(f"🎉 {reg_name} ची बायोमेट्रिक नोंदणी यशस्वी झाली आहे!")
            else:
                st.error("❌ कृपया नाव आणि फोटो दोन्ही गोष्टी पूर्ण करा.")

    with tab2:
        st.subheader("फक्त कॅмера समोर या - सिस्टीम स्वतः ओळखेल")
        if len(st.session_state['user_db']) == 0:
            st.warning("⚠️ आधी रजिस्ट्रेशन करा.")
        else:
            login_cam = st.camera_input("लॉगिनसाठी चेहऱ्याचा फोटो काढा", key="login_camera")
            if login_cam:
                with st.spinner("🔄 Scanning Face Database..."):
                    try:
                        login_img = Image.open(login_cam).convert('RGB')
                        login_resized = login_img.resize((300, 300))
                        match_found = False
                        identified_user = None
                        best_score = 1.0
                        
                        for name, base_img in st.session_state['user_db'].items():
                            base_resized = base_img.resize((300, 300))
                            diff = ImageChops.difference(base_resized, login_resized)
                            stat = ImageStat.Stat(diff)
                            diff_ratio = sum(stat.mean) / (3 * 255)
                            if diff_ratio < best_score:
                                best_score = diff_ratio
                                if diff_ratio < 0.45: 
                                    match_found = True
                                    identified_user = name
                        
                        if match_found:
                            st.session_state['authenticated'] = True
                            st.session_state['current_user'] = identified_user
                            st.rerun()
                        else:
                            st.error(f"❌ चेहरा ओळखता आला नाही!")
                    except Exception as e:
                        st.error(f"एरर: {e}")

# 🔓 PHASE 2: AUTOMATION CONTROL PANEL (FULL INTEGRATED ENGINE)
else:
    st.success(f"🔓 Authenticated Successfully as {st.session_state['current_user']}!")
    
    # इनपुट बॉक्स लपवण्यासाठी CSS
    st.markdown("<style>div[data-testid='stTextInput'] { display: none !important; }</style>", unsafe_allow_html=True)

    # --- 🎙️ JAVASCRIPT: THE ULTIMATE INTEGRATED ENGINE ---
    js_stable_engine = """
    <div id="voice-ui" style="padding:15px; background-color:#f0f2f6; border-radius:10px; margin-bottom:10px; text-align:center;">
        <p style="margin:0; font-weight:bold; color:#1f77b4; margin-bottom:10px;">🤖 Double Engine AI: <span id="speech-live" style="color:#333; font-weight:normal;">Listening continuously...</span></p>
        <button id="wakeup-btn" style="display:none; width:100%; padding:15px; background-color:#2ecc71; color:white; font-size:18px; font-weight:bold; border:none; border-radius:8px; cursor:pointer; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">🎤 Tap Here to Resume Mic</button>
    </div>

    <script>
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        let recognition;
        let actionExecuted = false; 

        function speakText(text) {
            window.speechSynthesis.cancel();
            let speech = new SpeechSynthesisUtterance(text);
            speech.lang = 'en-IN';
            speech.onend = () => setTimeout(() => { try { recognition.start(); } catch(e) {} }, 500);
            window.speechSynthesis.speak(speech);
        }

        function askWikipedia(term) {
            try { recognition.abort(); } catch(e) {}
            fetch(`https://en.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(term)}`)
            .then(r => r.json())
            .then(data => {
                let answer = data.extract || "Information not found.";
                document.getElementById("speech-live").innerText = answer;
                speakText(answer);
            });
        }

        function startFreshMic() {
            if (recognition) { try { recognition.abort(); } catch(e) {} }
            recognition = new SpeechRecognition();
            recognition.continuous = true;
            recognition.interimResults = true;
            recognition.lang = 'en-US';

            recognition.onresult = function(event) {
                let finalTranscript = '';
                let isFinal = false;
                for (let i = event.resultIndex; i < event.results.length; ++i) {
                    if (event.results[i].isFinal) {
                        finalTranscript += event.results[i][0].transcript;
                        isFinal = true;
                    }
                }
                
                if (isFinal) {
                    let cmd = finalTranscript.toLowerCase().trim();
                    document.getElementById("speech-live").innerText = cmd;
                    
                    if (cmd.includes("whatsapp")) { actionExecuted=true; window.open("intent://send/#Intent;package=com.whatsapp;scheme=whatsapp;end", "_blank"); recognition.abort(); }
                    else if (cmd.includes("youtube")) { actionExecuted=true; window.open("intent://www.youtube.com/#Intent;package=com.google.android.youtube;scheme=https;end", "_blank"); recognition.abort(); }
                    else { askWikipedia(cmd); }
                }
            };
            recognition.onend = () => { if (!actionExecuted) setTimeout(() => { try { recognition.start(); } catch(e) {} }, 500); };
            try { recognition.start(); } catch(e) {}
        }

        document.addEventListener("visibilitychange", () => {
            if (document.visibilityState === "visible" && actionExecuted) {
                document.getElementById("wakeup-btn").style.display = "block";
            }
        });

        document.getElementById("wakeup-btn").addEventListener("click", () => {
            actionExecuted = false;
            document.getElementById("wakeup-btn").style.display = "none";
            startFreshMic();
        });

        startFreshMic();
    </script>
    """
    components.html(js_stable_engine, height=220)

    st.write("---")
    if st.button("🛑 Lock System Manually", use_container_width=True):
        st.session_state['authenticated'] = False
        st.session_state['current_user'] = None
        st.rerun()