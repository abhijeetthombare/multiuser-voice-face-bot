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

st.title("🤖 Next-Gen Multi-User Voice & Face Bot (Pure Hands-Free)")
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
                                if diff_ratio < 0.45: 
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

# 🔓 PHASE 2: AUTOMATION CONTROL PANEL (100% STABLE FRONTEND VOICE)
else:
    st.success(f"🔓 Authenticated Successfully as {st.session_state['current_user']}!")
    st.markdown("🌐 **Status:** `माईक ऑन आहे. थेट बोला (उदा: 'Python open whatsapp')`")
    
    st.info("🎙️ Live Speech UI linked directly to Browser Speech Engine.")

    # --- 🎙️ JAVASCRIPT ULTRA STABLE VOICE INTERFACE (BYPASSING CHROME BLOCKER) ---
    js_stable_engine = """
    <div id="voice-ui" style="padding:15px; background-color:#f0f2f6; border-radius:10px; margin-bottom:10px;">
        <p style="margin:0; font-weight:bold; color:#1f77b4;">🗣️ Live Speech (तुमचा आवाज): <span id="speech-live" style="color:#333; font-weight:normal;">Waiting for voice...</span></p>
    </div>

    <script>
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            document.getElementById("speech-live").innerText = "Web Speech API not supported in this browser.";
        } else {
            const recognition = new SpeechRecognition();
            recognition.continuous = true;
            recognition.interimResults = true;
            recognition.lang = 'en-US';

            // 🚀 Chrome Security block bypass karnara solid function
            function forceExecuteIntent(appIntent, webFallback) {
                // Mic la 1.5 sekandasathi shaant karne jyamule browser la reload/loop cha shock basnaar nahi
                recognition.stop();
                
                try {
                    // Method 1: Direct location replacement (Best for Android Apps)
                    window.location.replace(appIntent);
                } catch(e) {
                    // Method 2: Flash Anchor Tag click simulation
                    const link = document.createElement('a');
                    link.href = appIntent;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                }

                // 🔄 1.5 सेकंदानंतर माईक पूर्णपणे रिसेट होऊन पुन्हा ऐकायला सुरुवात करेल
                setTimeout(() => {
                    try { recognition.start(); } catch(err) {}
                }, 1500);
            }

            recognition.onresult = function(event) {
                let interimTranscript = '';
                let finalTranscript = '';

                for (let i = event.resultIndex; i < event.results.length; ++i) {
                    if (event.results[i].isFinal) {
                        finalTranscript += event.results[i][0].transcript;
                    } else {
                        interimTranscript += event.results[i][0].transcript;
                    }
                }

                const currentText = finalTranscript || interimTranscript;
                document.getElementById("speech-live").innerText = currentText;
                
                const query = currentText.toLowerCase().trim();
                
                if (query.includes("python") || query.includes("paithen") || query.includes("py")) {
                    let cleanCmd = query.replace("python", "").replace("paithen", "").replace("py", "").trim();
                    
                    if (cleanCmd.includes("open") || cleanCmd.includes("start")) {
                        let app = cleanCmd.replace("open", "").replace("start", "").trim();
                        
                        // 🔥 NATIVE HARD FORCED INTENTS
                        if (app.includes("whatsapp")) {
                            forceExecuteIntent("intent://send/#Intent;package=com.whatsapp;scheme=whatsapp;end", "https://api.whatsapp.com/send");
                        } else if (app.includes("instagram") || app.includes("insta")) {
                            forceExecuteIntent("intent://instagram.com/#Intent;package=com.instagram.android;scheme=https;end", "https://instagram.com");
                        } else if (app.includes("youtube") || app.includes("yt")) {
                            forceExecuteIntent("intent://www.youtube.com/#Intent;package=com.google.android.youtube;scheme=https;end", "https://youtube.com");
                        } else if (app.includes("facebook") || app.includes("fb")) {
                            forceExecuteIntent("intent://www.facebook.com/#Intent;package=com.facebook.katana;scheme=https;end", "https://facebook.com");
                        } else if (app.includes("map") || app.includes("maps")) {
                            forceExecuteIntent("intent://maps.google.com/#Intent;package=com.google.android.apps.maps;scheme=https;end", "https://maps.google.com");
                        } else if (app.includes("mail") || app.includes("gmail")) {
                            forceExecuteIntent("intent://mail.google.com/#Intent;package=com.google.android.gm;scheme=https;end", "https://mail.google.com");
                        } else {
                            forceExecuteIntent("https://www.google.com/search?q=" + encodeURIComponent(app), "https://www.google.com/search?q=" + app);
                        }
                    }
                    // 📶 SYSTEM HARDWARE SETTINGS
                    else if (cleanCmd.includes("wifi") || cleanCmd.includes("wi-fi")) {
                        forceExecuteIntent("intent:#Intent;action=android.settings.WIFI_SETTINGS;end", "");
                    } else if (cleanCmd.includes("data") || cleanCmd.includes("internet")) {
                        forceExecuteIntent("intent:#Intent;action=android.settings.DATA_ROAMING_SETTINGS;end", "");
                    } else if (cleanCmd.includes("location") || cleanCmd.includes("gps")) {
                        forceExecuteIntent("intent:#Intent;action=android.settings.LOCATION_SOURCE_SETTINGS;end", "");
                    } else if (cleanCmd.includes("hotspot")) {
                        forceExecuteIntent("intent:#Intent;action=android.settings.TETHER_SETTINGS;end", "");
                    } else if (cleanCmd.includes("bluetooth")) {
                        forceExecuteIntent("intent:#Intent;action=android.settings.BLUETOOTH_SETTINGS;end", "");
                    }
                }
            };

            recognition.onend = function() {
                // Safe restart loop jyamule crash honar nahi
                setTimeout(() => {
                    try { recognition.start(); } catch(err) {}
                }, 500);
            };

            recognition.start();
        }
    </script>
    """
    components.html(js_stable_engine, height=120)

    st.write("---")
    if st.button("🛑 Lock System Manually", use_container_width=True):
        st.session_state['authenticated'] = False
        st.session_state['current_user'] = None
        st.rerun()