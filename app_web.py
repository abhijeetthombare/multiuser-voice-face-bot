import streamlit as st
import streamlit.components.v1 as components
import time
from PIL import Image, ImageChops, ImageStat

# --- १. PAGE SET-UP & THEME ---
st.set_page_config(page_title="Universal AI Hub", page_icon="🤖", layout="wide")
st.title("🤖 Next-Gen Voice Bot (Direct Name-Recall AI)")
st.write("---")

# --- २. SESSION STATES ---
if 'user_db' not in st.session_state: st.session_state['user_db'] = {} 
if 'authenticated' not in st.session_state: st.session_state['authenticated'] = False

# --- ३. LOGIC: ॲप उघडणे आणि माहिती सांगणे ---
if not st.session_state['authenticated']:
    st.write("आधी फेस रजिस्ट्रेशन करा...")
else:
    st.success(f"🔓 Hello {st.session_state.get('current_user', 'User')}, I am ready!")
    
    js_engine = """
    <div id="voice-ui" style="padding:15px; background-color:#f0f2f6; border-radius:10px;">
        <p>🗣️ AI: <span id="speech-live">Listening...</span></p>
    </div>

    <script>
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        let recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        function speakText(text) {
            window.speechSynthesis.cancel();
            let speech = new SpeechSynthesisUtterance(text);
            speech.lang = 'en-IN';
            window.speechSynthesis.speak(speech);
        }

        function askWikipedia(term) {
            document.getElementById("speech-live").innerText = "Searching: " + term;
            fetch(`https://en.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(term)}`)
            .then(r => r.json())
            .then(data => {
                let answer = data.extract || "Information not found.";
                document.getElementById("speech-live").innerText = answer;
                speakText(answer);
            });
        }

        recognition.onresult = function(event) {
            let command = event.results[event.results.length-1][0].transcript.toLowerCase().trim();
            document.getElementById("speech-live").innerText = command;
            
            // ॲप्स उघडण्यासाठी डायरेक्ट मॅपिंग
            if (command.includes("whatsapp")) window.open("intent://send/#Intent;package=com.whatsapp;scheme=whatsapp;end", "_blank");
            else if (command.includes("youtube")) window.open("intent://www.youtube.com/#Intent;package=com.google.android.youtube;scheme=https;end", "_blank");
            else if (command.includes("instagram")) window.open("intent://instagram.com/#Intent;package=com.instagram.android;scheme=https;end", "_blank");
            
            // नाव घेतलं की थेट माहिती (Wikipedia)
            else {
                askWikipedia(command);
            }
        };

        recognition.onend = () => { try { recognition.start(); } catch(e) {} };
        recognition.start();
    </script>
    """
    components.html(js_engine, height=200)