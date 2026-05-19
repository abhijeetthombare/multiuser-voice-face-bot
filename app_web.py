import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import io
import os
import time
from PIL import Image, ImageChops, ImageStat

# --- १. PAGE SET-UP & THEME ---
st.set_page_config(page_title="Universal AI Hub", page_icon="🤖", layout="wide")
st.title("🤖 Next-Gen Voice Bot (App Launcher + Multi-Lang AI)")
st.write("---")

# --- २. MULTI-USER SESSION STATES ---
if 'user_db' not in st.session_state: st.session_state['user_db'] = {} 
if 'current_user' not in st.session_state: st.session_state['current_user'] = None
if 'authenticated' not in st.session_state: st.session_state['authenticated'] = False

# --- ३. MAIN UI RENDERING ---
col1, col2 = st.columns(2)
with col1:
    status_text = f"🔓 UNLOCKED ({st.session_state['current_user']})" if st.session_state['authenticated'] else "LOCKED 🔒"
    st.metric(label="🔐 Security Status", value=status_text)
with col2:
    st.metric(label="👥 Registered Users", value=len(st.session_state['user_db']))

st.write("---")

# --- ४. REGISTRATION & LOGIN ---
if not st.session_state['authenticated']:
    tab1, tab2 = st.tabs(["📝 New User Registration", "🔑 Automatic Biometric Login"])
    with tab1:
        reg_name = st.text_input("तुमचे नाव टाका:").strip()
        reg_cam = st.camera_input("नोंदणीसाठी फोटो:", key="reg_camera")
        if st.button("Register Face Now"):
            if reg_name and reg_cam:
                st.session_state['user_db'][reg_name] = Image.open(reg_cam).convert('RGB')
                st.success("✅ नोंदणी यशस्वी!")
    with tab2:
        login_cam = st.camera_input("लॉगिनसाठी फोटो:", key="login_camera")
        if login_cam:
            login_img = Image.open(login_cam).convert('RGB')
            # (Face logic logic here)
            st.session_state['authenticated'] = True
            st.session_state['current_user'] = "Abhii"
            st.rerun()
else:
    st.success(f"🔓 Authenticated as {st.session_state['current_user']}!")
    
    # --- 🎙️ JAVASCRIPT: THE ULTIMATE INTEGRATED ENGINE ---
    js_engine = """
    <div id="voice-ui" style="padding:15px; background:#f0f2f6; border-radius:10px;">
        <p>🤖 AI Assistant: <span id="speech-live" style="font-weight:bold;">Listening...</span></p>
        <button id="wakeup-btn" style="display:none; width:100%; padding:10px; background:#2ecc71; color:white; border:none; border-radius:5px;">🎤 Resume Mic</button>
    </div>

    <script>
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        let recognition;
        let actionExecuted = false;

        function askWikipedia(term) {
            document.getElementById("speech-live").innerText = "Searching: " + term;
            // आधी मराठी चेक कर, नसेल तर इंग्लिश
            fetch(`https://mr.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(term)}`)
            .then(r => r.json())
            .then(data => {
                if (data.extract) { speakText(data.extract); }
                else {
                    fetch(`https://en.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(term)}`)
                    .then(r => r.json())
                    .then(d => speakText(d.extract || "No info found."));
                }
            });
        }

        function speakText(text) {
            window.speechSynthesis.cancel();
            let s = new SpeechSynthesisUtterance(text);
            s.lang = 'mr-IN'; // मराठीसाठी मराठी लँग्वेज
            s.onend = () => { try { recognition.start(); } catch(e) {} };
            window.speechSynthesis.speak(s);
        }

        function startMic() {
            recognition = new SpeechRecognition();
            recognition.continuous = true;
            recognition.lang = 'mr-IN'; // मराठी आवाजासाठी
            recognition.onresult = (event) => {
                let cmd = event.results[event.results.length-1][0].transcript.toLowerCase().trim();
                document.getElementById("speech-live").innerText = cmd;
                
                if (cmd.includes("whatsapp")) { actionExecuted=true; window.open("intent://send/#Intent;package=com.whatsapp;scheme=whatsapp;end", "_blank"); }
                else if (cmd.includes("youtube")) { actionExecuted=true; window.open("intent://www.youtube.com/#Intent;package=com.google.android.youtube;scheme=https;end", "_blank"); }
                else { askWikipedia(cmd); }
            };
            recognition.start();
        }

        document.addEventListener("visibilitychange", () => {
            if (document.visibilityState === "visible" && actionExecuted) document.getElementById("wakeup-btn").style.display = "block";
        });

        document.getElementById("wakeup-btn").onclick = () => {
            actionExecuted = false;
            document.getElementById("wakeup-btn").style.display = "none";
            startMic();
        };

        startMic();
    </script>
    """
    components.html(js_engine, height=250)

    if st.button("🛑 Lock System"):
        st.session_state['authenticated'] = False
        st.rerun()