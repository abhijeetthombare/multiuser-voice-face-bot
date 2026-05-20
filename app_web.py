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

st.title("🤖 Next-Gen Voice Bot (Stable Wikipedia AI)")
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
                st.success(f"🎉 {reg_name} ची बायोमेट्रिक नोंदणी यशस्वी झाली आहे! आता लॉगिन टॅबमध्ये जा.")
            else:
                st.error("❌ कृपया नाव आणि फोटो दोन्ही गोष्टी पूर्ण करा.")

    with tab2:
        st.subheader("फक्त कॅмера समोर या - सिस्टीम स्वतः ओळखेल")
        
        if len(st.session_state['user_db']) == 0:
            st.warning("⚠️ आधी रजिस्ट्रेशन टॅबमध्ये जाऊन किमान एका युझरची नोंदणी करा.")
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
                                # 🔥 सिक्युरिटी फिक्स: 0.18 (Strict Mode)
                                if diff_ratio < 0.18: 
                                    match_found = True
                                    identified_user = name
                        
                        if match_found:
                            st.session_state['authenticated'] = True
                            st.session_state['current_user'] = identified_user
                            st.rerun()
                        else:
                            st.error(f"❌ चेहरा ओळखता आला नाही! (Distance: {round(best_score, 2)})")
                    except Exception as e:
                        st.error(f"प्रमाणीकरण एरर: {e}")

# 🔓 PHASE 2: AUTOMATION CONTROL PANEL (WIKIPEDIA AI ENGINE)
else:
    st.success(f"🔓 Authenticated Successfully as {st.session_state['current_user']}!")
    
    st.markdown("<style>div[data-testid='stTextInput'] { display: none !important; }</style>", unsafe_allow_html=True)

    # --- 🎙️ JAVASCRIPT: THE ECHO-FREE WIKIPEDIA ENGINE ---
    js_stable_engine = """
    <div id="voice-ui" style="padding:15px; background-color:#f0f2f6; border-radius:10px; margin-bottom:10px; text-align:center;">
        <p style="margin:0; font-weight:bold; color:#1f77b4; margin-bottom:10px;">🤖 AI Assistant: <span id="speech-live" style="color:#333; font-weight:normal;">Listening continuously...</span></p>
        
        <button id="wakeup-btn" style="display:none; width:100%; padding:15px; background-color:#2ecc71; color:white; font-size:18px; font-weight:bold; border:none; border-radius:8px; cursor:pointer; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">🎤 Tap Here to Resume Mic</button>
    </div>

    <script>
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            document.getElementById("speech-live").innerText = "Web Speech API not supported.";
        } else {
            let recognition;
            let actionExecuted = false; 
            let isSpeaking = false; 

            // 🗣️ Text-to-Speech Function
            function speakText(text) {
                window.speechSynthesis.cancel();
                isSpeaking = true;
                
                let cleanTextForSpeech = text.replace(/[*#]/g, ''); 
                
                let speech = new SpeechSynthesisUtterance(cleanTextForSpeech);
                speech.lang = 'en-IN'; 
                speech.rate = 1.0; 
                
                speech.onend = function() {
                    isSpeaking = false;
                    document.getElementById("speech-live").innerHTML = "<span style='color:#2ecc71; font-weight:bold;'>🟢 AI is listening again...</span>";
                    setTimeout(startFreshMic, 500); 
                };

                speech.onerror = function() {
                    isSpeaking = false;
                    setTimeout(startFreshMic, 500);
                };
                
                window.speechSynthesis.speak(speech);
            }

            // 🌐 Wikipedia API Function (No API Key Required!)
            function askWikipedia(searchTerm) {
                try { recognition.abort(); } catch(e) {} 
                
                document.getElementById("speech-live").innerHTML = "<span style='color:#8e44ad; font-weight:bold;'>🔍 Searching Wikipedia for: </span>" + searchTerm + "...";

                fetch(`https://en.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(searchTerm)}`)
                .then(response => response.json())
                .then(data => {
                    let answer = "Sorry, I couldn't find accurate information about that.";
                    if (data.type === "standard" || data.type === "disambiguation") {
                        answer = data.extract; 
                    }
                    
                    document.getElementById("speech-live").innerHTML = "<span style='color:#8e44ad; font-weight:bold;'>🤖 Assistant: </span>" + answer;
                    speakText(answer); 
                })
                .catch(err => {
                    document.getElementById("speech-live").innerHTML = "<span style='color:#d32f2f; font-weight:bold;'>⚠️ Network Error!</span>";
                    speakText("Sorry, there was an internet error fetching data.");
                });
            }

            // 🎤 Main Mic Function
            function startFreshMic() {
                if (recognition) { try { recognition.abort(); } catch(e) {} }

                recognition = new SpeechRecognition();
                // 🔥 THE ONE-TIME FIX: continuous = false केल्यावर Android डुप्लिकेशन करणार नाही!
                recognition.continuous = false; 
                recognition.interimResults = true;
                recognition.lang = 'en-US';

                recognition.onresult = function(event) {
                    let transcript = "";
                    let isFinalCommand = false;

                    for (let i = 0; i < event.results.length; ++i) {
                        transcript += event.results[i][0].transcript;
                        if (event.results[i].isFinal) {
                            isFinalCommand = true;
                        }
                    }

                    document.getElementById("speech-live").innerText = transcript;
                    
                    if (isFinalCommand) {
                        const query = transcript.toLowerCase().trim();
                        
                        // 🔥 Strict trigger word check
                        if (query.includes("python") || query.includes("paithen")) {
                            let cleanCmd = query.replace("python", "").replace("paithen", "").replace("open", "").replace("start", "").trim();
                            
                            function fireIntent(intentUrl) {
                                actionExecuted = true; 
                                window.open(intentUrl, '_blank'); 
                                document.getElementById("speech-live").innerHTML = "<span style='color:#e67e22; font-weight:bold;'>⚡ App Opened! Come back and tap to resume.</span>";
                            }

                            // 📱 ॲप लाँचर फीचर्स (फक्त पूर्ण नावे)
                            if (cleanCmd.includes("whatsapp")) fireIntent("intent://send/#Intent;package=com.whatsapp;scheme=whatsapp;end");
                            else if (cleanCmd.includes("youtube")) fireIntent("intent://www.youtube.com/#Intent;package=com.google.android.youtube;scheme=https;end");
                            else if (cleanCmd.includes("instagram")) fireIntent("intent://instagram.com/#Intent;package=com.instagram.android;scheme=https;end");
                            else if (cleanCmd.includes("facebook")) fireIntent("intent://www.facebook.com/#Intent;package=com.facebook.katana;scheme=https;end");
                            else if (cleanCmd.includes("map") || cleanCmd.includes("maps")) fireIntent("intent://geo:0,0?q=maps#Intent;scheme=geo;end");
                            else if (cleanCmd.includes("wifi")) fireIntent("intent:#Intent;action=android.settings.WIFI_SETTINGS;end");
                            else if (cleanCmd.includes("bluetooth")) fireIntent("intent:#Intent;action=android.settings.BLUETOOTH_SETTINGS;end");
                            
                            // 🔍 चॅटबॉट सर्च (Wikipedia)
                            else if (cleanCmd.length > 1) {
                                let searchQuery = cleanCmd.replace("search", "").replace("who is", "").replace("what is", "").replace("tell me about", "").trim();
                                askWikipedia(searchQuery);
                            }
                        }
                    }
                };

                recognition.onend = function() {
                    if (!actionExecuted && !isSpeaking) {
                        setTimeout(() => { try { recognition.start(); } catch(err) {} }, 300);
                    }
                };

                try { recognition.start(); } catch(e) {}
            }

            // 🛡️ Watchdog Timer
            setInterval(() => {
                if (!actionExecuted && !isSpeaking && recognition) {
                    try { recognition.start(); } catch(e) {}
                }
            }, 5000);

            document.addEventListener("visibilitychange", function() {
                if (document.visibilityState === "visible" && actionExecuted === true) {
                    document.getElementById("wakeup-btn").style.display = "block";
                }
            });

            document.getElementById("wakeup-btn").addEventListener("click", function() {
                actionExecuted = false; 
                this.style.display = "none"; 
                document.getElementById("speech-live").innerHTML = "<span style='color:#2ecc71; font-weight:bold;'>🟢 AI is ACTIVE! Speak now...</span>";
                startFreshMic(); 
            });

            startFreshMic();
        }
    </script>
    """
    components.html(js_stable_engine, height=220)

    st.write("---")
    if st.button("🛑 Lock System Manually", use_container_width=True):
        st.session_state['authenticated'] = False
        st.session_state['current_user'] = None
        st.rerun()