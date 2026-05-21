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

st.title("🤖 Next-Gen Voice & Text Bot (Ultra-Secure AI)")
st.write("---")

# --- २. PERMANENT FACE DATABASE ---
if not os.path.exists("registered_faces"):
    os.makedirs("registered_faces")

if 'user_db' not in st.session_state:
    st.session_state['user_db'] = {} 
    for file in os.listdir("registered_faces"):
        if file.endswith((".jpg", ".jpeg", ".png")):
            name = os.path.splitext(file)[0]
            img_path = os.path.join("registered_faces", file)
            st.session_state['user_db'][name] = Image.open(img_path).convert('RGB')

# --- ३. AUTO-LOGIN CHECK ---
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

# --- ५. REGISTRATION & LOGIN TABS ---
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
            login_cam = st.camera_input("लॉगिनसाठी चेहऱ्याचा फोटो काढा", key="login_camera")
            
            if login_cam:
                with st.spinner("🔄 Scanning Face Database..."):
                    try:
                        login_img = Image.open(login_cam).convert('RGB')
                        login_resized = login_img.resize((300, 300))
                        
                        best_score = 1.0
                        best_match_name = None
                        
                        for name, base_img in st.session_state['user_db'].items():
                            base_resized = base_img.resize((300, 300))
                            diff = ImageChops.difference(base_resized, login_resized)
                            stat = ImageStat.Stat(diff)
                            diff_ratio = sum(stat.mean) / (3 * 255)
                            
                            if diff_ratio < best_score:
                                best_score = diff_ratio
                                best_match_name = name
                        
                        if best_score < 0.15 and best_match_name is not None:
                            st.session_state['authenticated'] = True
                            st.session_state['current_user'] = best_match_name
                            st.query_params["user"] = best_match_name
                            st.rerun()
                        else:
                            st.error(f"❌ चेहरा ओळखता आला नाही! (Distance: {round(best_score, 2)})\nदुसरा व्यक्ती किंवा चुकीचा प्रकाश असू शकतो.")
                    except Exception as e:
                        st.error(f"प्रमाणीकरण एरर: {e}")

# 🔓 PHASE 2: AUTOMATION CONTROL PANEL 
else:
    st.success(f"🔓 Authenticated Successfully as {st.session_state['current_user']}! (Your session is permanently active)")
    
    active_user = str(st.session_state['current_user'])

    # ==========================================
    # 👑 ADMIN CONTROL PANEL 
    # ==========================================
    ADMIN_NAME = "Abhijeet"  
    
    if active_user == ADMIN_NAME:
        with st.expander("👑 Admin Control Panel (View & Delete Users)", expanded=False):
            st.info("System Admin Access: तुम्ही सिस्टीममधील कोणतेही युझर अकाऊंट डिलीट करू शकता.")
            for u_name in list(st.session_state['user_db'].keys()):
                col_u, col_d = st.columns([3, 1])
                with col_u:
                    st.write(f"👤 **{u_name}**")
                with col_d:
                    if st.button(f"🗑️ Delete User", key=f"del_{u_name}", use_container_width=True):
                        del st.session_state['user_db'][u_name]
                        file_path = os.path.join("registered_faces", f"{u_name}.jpg")
                        if os.path.exists(file_path):
                            os.remove(file_path)
                        st.success(f"'{u_name}' चे खाते यशस्वीरित्या डिलीट झाले!")
                        time.sleep(1)
                        st.rerun()
        st.write("---")

    lang_choice = st.radio("🗣️ Choose Bot Language / भाषा निवडा:", ["English", "मराठी"], horizontal=True)
    lang_map = { "English": "en-IN", "मराठी": "mr-IN" }
    stt_lang = lang_map[lang_choice]

    # --- 🎙️ JAVASCRIPT: GEMINI CHATBOT ENGINE (ANTI TUN-TUN EDITION) ---
    js_template = """
    <div id="voice-ui" style="padding:15px; background-color:#f0f2f6; border-radius:10px; margin-bottom:10px; text-align:center; box-shadow: inset 0 0 10px rgba(0,0,0,0.05);">
        <p style="margin:0; font-weight:bold; color:#1f77b4; margin-bottom:15px;">🤖 Gemini Chat AI: <span id="speech-live" style="color:#333; font-weight:normal;">Listening quietly... Speak when ready.</span></p>
        
        <div style="display: flex; gap: 10px; margin-bottom: 15px;">
            <input type="text" id="text-input" placeholder="येथे टाईप करा किंवा बोला..." style="flex: 1; padding: 12px; border-radius: 8px; border: 1px solid #ccc; font-size:16px;">
            <button id="send-btn" style="padding: 12px 20px; background-color: #3498db; color: white; border: none; border-radius: 8px; font-weight:bold; cursor: pointer; font-size:16px;">Send</button>
        </div>

        <button id="refresh-btn" style="width:100%; padding:12px; background-color:#f39c12; color:white; font-size:16px; font-weight:bold; border:none; border-radius:8px; cursor:pointer; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom:10px;">🔄 Refresh / Wake Up Voice</button>
        <button id="wakeup-btn" style="display:none; width:100%; padding:15px; background-color:#2ecc71; color:white; font-size:18px; font-weight:bold; border:none; border-radius:8px; cursor:pointer; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">🎤 Tap Here to Resume Mic</button>
    </div>

    <div id="history-container" style="background-color:#ffffff; border-radius:10px; padding:15px; max-height: 250px; overflow-y: auto; box-shadow: 0 2px 5px rgba(0,0,0,0.1); text-align:left;">
        <div style="display:flex; justify-content:space-between; align-items:center; border-bottom: 2px solid #f0f2f6; padding-bottom: 5px; margin-bottom: 10px;">
            <h4 style="margin:0; color:#2c3e50;">📜 USER_NAME's Chat History</h4>
            <button onclick="clearHistory()" style="background:#e74c3c; color:white; border:none; border-radius:5px; padding:5px 10px; cursor:pointer; font-size:12px;">🗑️ Clear</button>
        </div>
        <div id="history-list"></div>
    </div>

    <script>
        // 🔥 तुझी खरी नवीन API Key टाकून दे भावा!
        const GEMINI_API_KEY = "AIzaSyDzMF5GpLFp1LMI_AHpTbXiVrlTD1o0cYQ"; 
        
        const CURRENT_USER = 'USER_NAME';
        const HISTORY_KEY = 'abhii_bot_history_' + CURRENT_USER; 
        const STT_LANG = 'LANG_STT';

        function updateHistoryUI() {
            let history = JSON.parse(localStorage.getItem(HISTORY_KEY)) || [];
            let html = "";
            if (history.length === 0) {
                html = "<p style='color:#7f8c8d; font-size:14px; text-align:center;'>No history yet. Start speaking or typing!</p>";
            } else {
                history.forEach(item => {
                    html += `
                        <div style="background:#f8f9fa; padding:10px; margin-bottom:8px; border-radius:8px; border-left: 4px solid #1f77b4;">
                            <div style="font-weight:bold; color:#2980b9; margin-bottom:4px;">👤 ${CURRENT_USER}: ${item.query}</div>
                            <div style="color:#444; font-size:14px;">🤖 Gemini: ${item.response}</div>
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
        let recognition;
        let actionExecuted = false; 
        let isSpeaking = false; 
        let isListening = false;
        let speechTimeout;

        function safeStartMic() {
            if (!isListening && !isSpeaking && !actionExecuted && recognition) {
                try {
                    recognition.start();
                } catch (e) {
                    console.log("Mic running:", e);
                }
            }
        }

        function speakText(text) {
            window.speechSynthesis.cancel();
            isSpeaking = true;
            if (recognition) { try { recognition.abort(); } catch(e) {} }
            
            let cleanTextForSpeech = text.replace(/[*#]/g, ''); 
            let speech = new SpeechSynthesisUtterance(cleanTextForSpeech);
            speech.lang = STT_LANG; 
            speech.rate = 1.0; 
            
            speech.onstart = function() {
                isSpeaking = true;
            };
            
            speech.onend = function() {
                isSpeaking = false;
                document.getElementById("speech-live").innerHTML = "<span style='color:#2ecc71; font-weight:bold;'>🟢 AI is listening again...</span>";
                setTimeout(safeStartMic, 600); 
            };
            
            speech.onerror = function() {
                isSpeaking = false;
                setTimeout(safeStartMic, 600);
            };
            window.speechSynthesis.speak(speech);
        }

        function askGeminiChat(searchTerm) {
            // 🔥 रिकामी कमांड असेल तर सरळ ब्लॉक करा! (नो टुन टुन)
            if (!searchTerm || searchTerm.trim().length < 2) return;

            if (recognition) { try { recognition.abort(); } catch(e) {} } 
            document.getElementById("speech-live").innerHTML = "<span style='color:#8e44ad; font-weight:bold;'>🧠 Gemini is thinking...</span>";
            const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${GEMINI_API_KEY}`;
            
            let langInstruction = STT_LANG === 'mr-IN' ? "Reply in pure conversational Marathi language." : "Reply in conversational English.";
            const prompt = `You are the user's friendly AI assistant. The user says: "${searchTerm}". ${langInstruction} Keep your answer short, friendly, and conversational (max 2-3 sentences). Do not use asterisks or markdown.`;

            fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ contents: [{ parts: [{ text: prompt }] }] })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    let errMsg = "API Key Error. Please put a valid Gemini API Key.";
                    document.getElementById("speech-live").innerText = errMsg;
                    return;
                }
                let answer = "Sorry, I didn't get that.";
                if (data.candidates && data.candidates.length > 0) {
                    answer = data.candidates[0].content.parts[0].text;
                }
                document.getElementById("speech-live").innerHTML = "<span style='color:#2ecc71; font-weight:bold;'>💬 </span>" + answer;
                saveHistory(searchTerm, answer); 
                speakText(answer); 
            })
            .catch(err => {
                document.getElementById("speech-live").innerHTML = "<span style='color:#d32f2f; font-weight:bold;'>⚠️ Network Error!</span>";
            });
        }

        document.getElementById("send-btn").addEventListener("click", function() {
            let textVal = document.getElementById("text-input").value;
            if(textVal.trim() !== "") {
                askGeminiChat(textVal);
                document.getElementById("text-input").value = ""; 
            }
        });

        document.getElementById("text-input").addEventListener("keypress", function(e) {
            if(e.key === 'Enter') {
                document.getElementById("send-btn").click();
            }
        });

        function processVoiceInput(finalTranscript) {
            const query = finalTranscript.toLowerCase().trim();
            
            // 🔥 जर फक्त कचरा आवाज असेल आणि 'पायथन' नसेल, तर ब्लॉक करा
            if (query.length < 3) return;

            if (query.includes("python") || query.includes("paithen") || query.includes("पायथन") || query.includes("पायथॉन")) {
                let cleanCmd = query.replace(/python|paithen|open|start|पायथन|पायथॉन|उघडा|चालू करा/g, "").trim();
                
                function fireIntent(intentUrl, appName) {
                    actionExecuted = true; 
                    if (recognition) { try { recognition.abort(); } catch(e) {} }
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
                    askGeminiChat(cleanCmd.trim());
                }
            }
        }

        function startFreshMic() {
            if (isSpeaking || actionExecuted) return;
            if (recognition) { try { recognition.abort(); } catch(e) {} }

            if (!SpeechRecognition) return;

            recognition = new SpeechRecognition();
            recognition.continuous = true; 
            recognition.interimResults = true; 
            recognition.lang = STT_LANG; 

            recognition.onstart = function() {
                isListening = true;
                document.getElementById("speech-live").innerHTML = "<span style='color:#2ecc71; font-weight:bold;'>🟢 AI Online & Silent... Speak now</span>";
            };

            recognition.onresult = function(event) {
                if (isSpeaking) return; 
                
                let interimTranscript = "";
                for (let i = event.resultIndex; i < event.results.length; ++i) {
                    interimTranscript += event.results[i][0].transcript;
                }
                
                // 🔥 फक्त व्हॅलिड शब्दांसाठीच यूआय अपडेट करा आणि टायमर लावा
                if (interimTranscript.trim().length >= 2) {
                    document.getElementById("speech-live").innerText = interimTranscript;
                    
                    clearTimeout(speechTimeout);
                    // 🔥 १.५ सेकंद (1500ms) चा रिलॅक्स टायमर दिलेला आहे
                    speechTimeout = setTimeout(() => {
                        processVoiceInput(interimTranscript);
                    }, 1500);
                }
            };

            recognition.onend = function() {
                isListening = false;
                if (!actionExecuted && !isSpeaking) {
                    setTimeout(safeStartMic, 600); 
                }
            };
            
            safeStartMic();
        }

        document.getElementById("refresh-btn").addEventListener("click", function() {
            actionExecuted = false;
            isSpeaking = false;
            isListening = false;
            clearTimeout(speechTimeout);
            window.speechSynthesis.cancel(); 
            if (recognition) { try { recognition.abort(); } catch(e) {} }
            let unlockSpeech = new SpeechSynthesisUtterance('');
            window.speechSynthesis.speak(unlockSpeech);
            document.getElementById("speech-live").innerHTML = "<span style='color:#e67e22; font-weight:bold;'>🔄 Refreshed! Speak now...</span>";
            setTimeout(startFreshMic, 400); 
        });

        document.addEventListener("visibilitychange", function() {
            if (document.visibilityState === "visible" && actionExecuted === true) {
                document.getElementById("wakeup-btn").style.display = "block";
            }
        });

        document.getElementById("wakeup-btn").addEventListener("click", function() {
            actionExecuted = false; 
            isListening = false;
            this.style.display = "none"; 
            document.getElementById("speech-live").innerHTML = "<span style='color:#2ecc71; font-weight:bold;'>🟢 AI is ACTIVE! Speak now...</span>";
            startFreshMic(); 
        });

        if (SpeechRecognition) {
            startFreshMic();
        } else {
            document.getElementById("speech-live").innerText = "Web Speech API not supported.";
        }
    </script>
    """
    
    js_final = js_template.replace("USER_NAME", active_user).replace("LANG_STT", stt_lang)
    
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