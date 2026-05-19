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
                        st.error(f"प्रмаणीकरण एरर: {e}")

# 🔓 PHASE 2: AUTOMATION CONTROL PANEL (100% STABLE FRONTEND VOICE)
else:
    st.success(f"🔓 Authenticated Successfully as {st.session_state['current_user']}!")
    
    # टेक्स्ट बॉक्स लपवण्यासाठी कडक CSS
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

    # --- 🎙️ JAVASCRIPT ULTRA STABLE VOICE INTERFACE (DIRECT DEEP LINKS) ---
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

            // 🚀 मूळ मोबाईल ॲप्स आणि हार्डवेअर डायरेक्ट ट्रिगर करणारे फंक्शन
            function launchDirectIntent(targetUrl) {
                recognition.stop(); // ब्राउझर सिक्युरिटी ब्लॉक टाळण्यासाठी तात्पुरते स्टॉप
                
                // डायरेक्ट लोकेशन चेंज (Chrome याला ब्लॉक करू शकत नाही)
                window.location.href = targetUrl;

                // १.५ सेकंदानंतर माईक पूर्ण फ्रेश आणि कंटीन्युअस सुरू होईल
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
                        
                        // 🔥 मोबाईल ओरिजिनल ॲप्स डायरेक्ट ओपनर लिंक्स (No Google Search!)
                        if (app.includes("whatsapp")) {
                            launchDirectIntent("whatsapp://send");
                        } else if (app.includes("instagram") || app.includes("insta")) {
                            launchDirectIntent("instagram://app");
                        } else if (app.includes("youtube") || app.includes("yt")) {
                            launchDirectIntent("youtube://");
                        } else if (app.includes("facebook") || app.includes("fb")) {
                            launchDirectIntent("fb://");
                        } else if (app.includes("map") || app.includes("maps")) {
                            launchDirectIntent("geo:0,0?q=maps");
                        } else if (app.includes("mail") || app.includes("gmail")) {
                            launchDirectIntent("googlegmail://");
                        } else {
                            launchDirectIntent("https://www.google.com/search?q=" + encodeURIComponent(app));
                        }
                    }
                    // 📶 मोबाईल सिस्टीम हार्डवेअर थेट सेटिंग्ज
                    else if (cleanCmd.includes("wifi") || cleanCmd.includes("wi-fi")) {
                        launchDirectIntent("intent:#Intent;action=android.settings.WIFI_SETTINGS;end");
                    } else if (cleanCmd.includes("data") || cleanCmd.includes("internet")) {
                        launchDirectIntent("intent:#Intent;action=android.settings.DATA_ROAMING_SETTINGS;end");
                    } else if (cleanCmd.includes("location") || cleanCmd.includes("gps")) {
                        launchDirectIntent("intent:#Intent;action=android.settings.LOCATION_SOURCE_SETTINGS;end");
                    } else if (cleanCmd.includes("hotspot")) {
                        launchDirectIntent("intent:#Intent;action=android.settings.TETHER_SETTINGS;end");
                    } else if (cleanCmd.includes("bluetooth")) {
                        launchDirectIntent("intent:#Intent;action=android.settings.BLUETOOTH_SETTINGS;end");
                    }
                }
            };

            recognition.onend = function() {
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