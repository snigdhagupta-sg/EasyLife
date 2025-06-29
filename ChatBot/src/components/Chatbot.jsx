import { useState, useEffect, useRef } from "react";
import "./Chatbot.css";

const languageOptions = {
  hi: { label: "Hindi", code: "hi-IN", placeholder: "अपना सवाल लिखें...", title: "🧠 ग्रामीण वित्त सहायक" },
  en: { label: "English", code: "en-US", placeholder: "Type your question...", title: "🧠 Rural Finance Assistant" },
  mr: { label: "Marathi", code: "mr-IN", placeholder: "आपला प्रश्न टाका...", title: "🧠 ग्रामीण वित्त सहाय्यता" },
  ta: { label: "Tamil", code: "ta-IN", placeholder: "உங்கள் கேள்வியை உள்ளிடவும்...", title: "🧠 கிராமத்து நிதி உதவி" },
};

export default function Chatbot() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [lang, setLang] = useState("hi");
  const recognitionRef = useRef(null);

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return;
    const recognition = new SpeechRecognition();
    recognition.lang = languageOptions[lang].code;
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    recognition.onresult = (event) => setInput(event.results[0][0].transcript);
    recognitionRef.current = recognition;
  }, [lang]);

  const startListening = () => recognitionRef.current?.start();
  const speak = (text) => {
    const synth = window.speechSynthesis;
    if (!synth) return;
    const utter = new SpeechSynthesisUtterance(text);
    utter.lang = languageOptions[lang].code;
    utter.rate = 1.1;
    synth.speak(utter);
  };

  const handleSend = async () => {
    if (!input.trim()) return;
    const userMsg = { role: "user", content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    try {
      const res = await fetch("http://localhost:8000/ask", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input, lang })
      });
      const { reply } = await res.json();
      const botMsg = { role: "bot", content: reply };
      setMessages(prev => [...prev, botMsg]);
      speak(reply);
    } catch (e) {
      const errText = {
        hi: "कुछ गलत हो गया है, बाद में आज़माएँ।",
        en: "Something went wrong. Please try later.",
        mr: "काही चुकलं, नंतर प्रयत्न करा.",
        ta: "செயலில் பிழை. பிறகு முயற்சிக்கவும்."
      };
      const err = errText[lang] || errText.en;
      setMessages(prev => [...prev, { role: "bot", content: err }]);
      speak(err);
    }
  };

  const { placeholder, title } = languageOptions[lang];

  return (
    <div className="chatbot-page">
      <div className="chatbot-card">
        <h1 className="chatbot-title">{title}</h1>
        <div className="controls">
          <select value={lang} onChange={e => setLang(e.target.value)} className="lang-select">
            {Object.entries(languageOptions).map(([k, o]) => <option key={k} value={k}>{o.label}</option>)}
          </select>
          <button onClick={startListening} className="mic-button" title={languageOptions[lang].label}>🎤</button>
        </div>
        <div className="chatbot-box">
          {messages.map((msg, i) => (
            <div key={i} className={`message-row ${msg.role}-row`}>
              <div className="avatar">{msg.role === "user" ? "🙂" : "🤖"}</div>
              <div className={`chat-message ${msg.role}-msg`}>{msg.content}</div>
            </div>
          ))}
        </div>
        <div className="input-area">
          <input type="text" value={input} onChange={e => setInput(e.target.value)} placeholder={placeholder} />
          <button onClick={handleSend} className="send-button">{lang === 'hi' ? 'भेजें' : 'Send'}</button>
        </div>
      </div>
    </div>
  );
}
