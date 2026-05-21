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

st.title("🤖 Next-Gen Voice Bot (Ultra-Secure Multi-Language AI)")
st.write("---")

# --- २. PERMANENT FACE DATABASE (कायमस्वरूपी फोल्डर) ---
if not os.path.exists("registered_faces"):
    os.makedirs("registered_faces")

if 'user_db' not in st.session_state:
    st.session_state['user_db'] = {} 
    for file in os.listdir("registered_faces"):
        if file.endswith((".jpg", ".jpeg", ".png")):
            name = os.path.splitext(file)[0]
            img_path = os.path.join("registered_faces", file)
            st.session_state['user_db'][name] = Image.open(img_path).convert('RGB')

# --- ३. AUTO-LOGIN CHECK (URL Token) ---
if 'user' in st.query_params:
    st.session_state['authenticated'] = True
    st.session_state['current_user'] = st.query_params['user']
elif 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
    st.session_state['current_user'] = None

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
                
                save_path = os.path.join("registered_faces", f"{reg_name}.jpg")
                reg_image.save(save_path)
                
                st.success(f"🎉 {reg_name} ची बायोमेट्रिक नोंदणी कायमस्वरूपी यशस्वी झाली आहे! आता लॉगिन टॅबमध्ये जा.")
            else:
                st.error("❌ कृपया नाव आणि फोटो दोन्ही गोष्टी पूर्ण करा.")

    with tab2:
        st.subheader("फक्त कॅмера समोर या - सिस्टीम स्वतः ओळखेल")
        
        if len(st.session_state['user_db']) == 0:
            st.warning("⚠️ आधी रजिस्ट्रेशन टॅबमध्ये जाऊन किमान एका युझरची नोंदणी करा.")
        else:
            login_cam = st.camera_input("लॉगिनसाठी चेहऱ्याचा फोटो काढा (चष्मा नको!)", key="login_camera")
            
            if login_cam:
                with st.spinner("🔄 Scanning Face Database..."):
                    try:
                        login_img = Image.open(login_cam).convert('RGB')
                        login_resized = login_img.resize((300, 300))
                        
                        best_score = 1.0
                        best_match_name = None
                        
                        # 🔥 नवीन लॉजिक: आधी सर्वात 'Best Match' शोधा
                        for name, base_img in st.session_state['user_db'].items():
                            base_resized = base_img.resize((300, 300))
                            diff = ImageChops.difference(base_resized, login_resized)
                            stat = ImageStat.Stat(diff)
                            diff_ratio = sum(stat.mean) / (3 * 255)
                            
                            if diff_ratio < best_score:
                                best_score = diff_ratio
                                best_match_name = name
                        
                        # 🔥 मिलिटरी ग्रेड सिक्युरिटी: 0.10 (Ultra Strict Mode)
                        # जर थोडाही बदल (चष्मा/दुसरा माणूस) असेल, तर स्कोर 0.10 च्या वर जाईल आणि रिजेक्ट होईल!
                        if best_score < 0.10 and best_match_name is not None:
                            st.session_state['authenticated'] = True
                            st.session_state['current_user'] = best_match_name
                            st.query_params["user"] = best_match_name
                            st.rerun()
                        else:
                            st.error(f"❌ चेहरा ओळखता आला नाही! (सुरक्षा नकार - Distance: {round(best_score, 2)})\nकृपया चष्मा काढला आहे आणि प्रकाश योग्य आहे याची खात्री करा.")
                    except Exception as e:
                        st.error(f"प्रमाणीकरण एरर: {e}")

# 🔓 PHASE 2: AUTOMATION CONTROL PANEL 
else:
    st.success(f"🔓 Authenticated Successfully as {st.session_state['current_user']}! (Your session is permanently active)")
    
    lang_choice = st.radio("🗣️ Choose Bot Language / भाषा निवडा:", ["English", "मराठी"], horizontal=True)
    
    lang_map = {
        "English": ("en-IN", "en"),
        "मराठी": ("mr-IN", "mr")
    }
    stt_lang, wiki_lang = lang_map[lang_choice]

    st.markdown("<style>div[data-testid='stTextInput'] { display: none !important; }</style>", unsafe_allow_html=True)

    active_user = str(st.session_state['current_user'])

    # --- 🎙️ JAVASCRIPT: PRIVATE HISTORY & MULTI-LINGUAL WIKIPEDIA ENGINE ---
    js_template = """
    <div id="voice-ui" style="padding:15px; background-color:#f0f2f6; border-radius:10px; margin-bottom:10px; text-align:center; box-shadow: inset 0 0 10px rgba(0,0,0,0.05);">
        <p style="margin:0; font-weight:bold; color:#1f77b4; margin-bottom:15px;">🤖 AI Assistant: <span id="speech-live" style="color:#333; font-weight:normal;">Listening continuously...</span></p>
        
        <button id="refresh-btn" style="width:100%; padding:12px; background-color:#f39c12; color:white; font-size:16px; font-weight:bold; border:none; border-radius:8px; cursor:pointer; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom:10px;">🔄 Refresh / Wake Up Voice</button>
        <button id="wakeup-btn" style="display:none; width:100%; padding:15px; background-color:#2ecc71; color:white; font-size:18px; font-weight:bold; border:none; border-radius:8px; cursor:pointer; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">🎤 Tap Here to Resume Mic</button>
    </div>

    <div id="history-container" style="background-color:#ffffff; border-radius:10px; padding:15px; max-height: 250px; overflow-y: auto; box-shadow: 0 2px 5px rgba(0,0,0,0.1); text-align:left;">
        <div style="display:flex; justify-content:space-between; align-items:center; border-bottom: 2px solid #f0f2f6; padding-bottom: 5px; margin-bottom: 10px;">
            <h4 style="margin:0; color:#2c3e50;">📜 USER_NAME's Search History</h4>
            <button onclick="clearHistory()" style="background:#e74c3c; color:white; border:none; border-radius:5px; padding:5px 10px; cursor:pointer; font-size:12px;">🗑️ Clear</button>
        </div>
        <div id="history-list"></div>
    </div>

    <script>
        const CURRENT_USER = 'USER_NAME';
        const HISTORY_KEY = 'abhii_bot_history_' + CURRENT_USER; 
        const STT_LANG = 'LANG_STT';
        const WIKI_LANG = 'LANG_WIKI';

        function updateHistoryUI() {
            let history = JSON.parse(localStorage.getItem(HISTORY_KEY)) || [];
            let html = "";
            if (history.length === 0) {
                html = "<p style='color:#7f8c8d; font-size:14px; text-align:center;'>No history yet. Start speaking!</p>";
            } else {
                history.forEach(item => {
                    html += `
                        <div style="background:#f8f9fa; padding:10px; margin-bottom:8px; border-radius:8px; border-left: 4px solid #1f77b4;">
                            <div style="font-weight:bold; color:#2980b9; margin-bottom:4px;">🗣️ ${CURRENT_USER}: ${item.query}</div>
                            <div style="color:#444; font-size:14px;">🤖 AI: ${item.response}</div>
                        </div>`;
                });
            }
            document.getElementById('history-list').innerHTML = html;
        }

        function saveHistory(query, response) {
            let history = JSON.parse(localStorage.getItem(HISTORY_KEY)) || [];
            history.unshift({query: query, response: response}); 
            if(history.length > 30) history.pop(); 
            localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
            updateHistoryUI();
        }

        function clearHistory() {
            localStorage.removeItem(HISTORY_KEY);
            updateHistoryUI();
        }

        updateHistoryUI();

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            document.getElementById("speech-live").innerText = "Web Speech API not supported.";
        } else {
            let recognition;
            let actionExecuted = false; 
            let isSpeaking = false; 

            function speakText(text) {
                window.speechSynthesis.cancel();
                isSpeaking = true;
                
                if (recognition) { try { recognition.abort(); } catch(e) {} }
                
                let cleanTextForSpeech = text.replace(/[*#]/g, ''); 
                let speech = new SpeechSynthesisUtterance(cleanTextForSpeech);
                speech.lang = STT_LANG; 
                speech.rate = 1.0; 
                
                speech.onstart = function() {
                    if (recognition) { try { recognition.abort(); } catch(e) {} }
                };

                speech.onend = function() {
                    isSpeaking = false;
                    document.getElementById("speech-live").innerHTML = "<span style='color:#2ecc71; font-weight:bold;'>🟢 AI is listening again...</span>";
                    setTimeout(startFreshMic, 800); 
                };

                speech.onerror = function() {
                    isSpeaking = false;
                    setTimeout(startFreshMic, 800);
                };
                
                window.speechSynthesis.speak(speech);
            }

            function askWikipedia(searchTerm) {
                if (recognition) { try { recognition.abort(); } catch(e) {} } 
                
                let formattedTerm = searchTerm.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join('_');
                
                document.getElementById("speech-live").innerHTML = "<span style='color:#8e44ad; font-weight:bold;'>🔍 Searching Wikipedia for: </span>" + searchTerm + "...";

                fetch(`https://${WIKI_LANG}.wikipedia.org/api/rest_v1/page/summary/${formattedTerm}`)
                .then(response => {
                    if (!response.ok) throw new Error("Not Found");
                    return response.json();
                })
                .then(data => {
                    let answer = "Sorry, I couldn't find accurate information about that.";
                    if (data.type === "standard" || data.type === "disambiguation") {
                        answer = data.extract; 
                    }
                    
                    document.getElementById("speech-live").innerHTML = "<span style='color:#2ecc71; font-weight:bold;'>💬 </span>" + answer;
                    saveHistory(searchTerm, answer); 
                    speakText(answer); 
                })
                .catch(err => {
                    let errMsg = "Sorry, information not found for '" + searchTerm + "'. Try speaking just the name clearly.";
                    document.getElementById("speech-live").innerHTML = "<span style='color:#d32f2f; font-weight:bold;'>⚠️ </span>" + errMsg;
                    saveHistory(searchTerm, errMsg); 
                    speakText(errMsg);
                });
            }

            function startFreshMic() {
                if (isSpeaking) return;
                if (recognition) { try { recognition.abort(); } catch(e) {} }

                recognition = new SpeechRecognition();
                recognition.continuous = false; 
                recognition.interimResults = true;
                recognition.lang = STT_LANG; 

                recognition.onresult = function(event) {
                    if (isSpeaking) return; 

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
                        
                        if (query.includes("python") || query.includes("paithen") || query.includes("पायथन") || query.includes("पायथॉन")) {
                            let cleanCmd = query.replace(/python|paithen|open|start|पायथन|पायथॉन|उघडा|चालू करा/g, "").trim();
                            
                            function fireIntent(intentUrl, appName) {
                                actionExecuted = true; 
                                saveHistory(query, `Opened ${appName} App ⚡`); 
                                window.open(intentUrl, '_blank'); 
                                document.getElementById("speech-live").innerHTML = "<span style='color:#e67e22; font-weight:bold;'>⚡ App Opened! Come back and tap to resume.</span>";
                            }

                            if (cleanCmd.includes("whatsapp") || cleanCmd.includes("व्हॉट्सॲप")) fireIntent("intent://send/#Intent;package=com.whatsapp;scheme=whatsapp;end", "WhatsApp");
                            else if (cleanCmd.includes("youtube") || cleanCmd.includes("यूट्यूब")) fireIntent("intent://www.youtube.com/#Intent;package=com.google.android.youtube;scheme=https;end", "YouTube");
                            else if (cleanCmd.includes("instagram") || cleanCmd.includes("इन्स्टाग्राम")) fireIntent("intent://instagram.com/#Intent;package=com.instagram.android;scheme=https;end", "Instagram");
                            else if (cleanCmd.includes("facebook") || cleanCmd.includes("फेसबुक")) fireIntent("intent://www.facebook.com/#Intent;package=com.facebook.katana;scheme=https;end", "Facebook");
                            else if (cleanCmd.includes("map") || cleanCmd.includes("maps") || cleanCmd.includes("मॅप्स")) fireIntent("intent://geo:0,0?q=maps#Intent;scheme=geo;end", "Google Maps");
                            else if (cleanCmd.includes("wifi") || cleanCmd.includes("वायफाय")) fireIntent("intent:#Intent;action=android.settings.WIFI_SETTINGS;end", "WiFi Settings");
                            else if (cleanCmd.includes("bluetooth") || cleanCmd.includes("ब्लूटूथ")) fireIntent("intent:#Intent;action=android.settings.BLUETOOTH_SETTINGS;end", "Bluetooth Settings");
                            
                            else if (cleanCmd.length > 1) {
                                let searchQuery = cleanCmd.replace(/search|who is|what is|tell me about|शोध|कोण आहे|माहिती सांग/g, "").trim();
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

            document.getElementById("refresh-btn").addEventListener("click", function() {
                actionExecuted = false;
                isSpeaking = false;
                window.speechSynthesis.cancel(); 
                
                let unlockSpeech = new SpeechSynthesisUtterance('');
                window.speechSynthesis.speak(unlockSpeech);

                document.getElementById("speech-live").innerHTML = "<span style='color:#e67e22; font-weight:bold;'>🔄 Refreshed! Voice Unlocked. Speak now...</span>";
                startFreshMic(); 
            });

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
    
    js_final = js_template.replace("USER_NAME", active_user).replace("LANG_STT", stt_lang).replace("LANG_WIKI", wiki_lang)
    
    components.html(js_final, height=600)

    st.write("---")
    
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    
    with col_btn1:
        if st.button("🔒 Lock System", use_container_width=True):
            st.session_state['authenticated'] = False
            st.query_params.clear() 
            st.rerun()
            
    with col_btn2:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state['authenticated'] = False
            st.session_state['current_user'] = None 
            st.query_params.clear() 
            st.rerun()
            
    with col_btn3:
        if st.button("🗑️ Delete My Account", use_container_width=True):
            user_to_delete = st.session_state['current_user']
            
            if user_to_delete in st.session_state['user_db']:
                del st.session_state['user_db'][user_to_delete]
                
            file_path = os.path.join("registered_faces", f"{user_to_delete}.jpg")
            if os.path.exists(file_path):
                os.remove(file_path)
                
            st.session_state['authenticated'] = False
            st.session_state['current_user'] = None 
            st.query_params.clear() 
            st.rerun()