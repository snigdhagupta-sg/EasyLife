import React, { useState } from "react";
import axios from "axios";
import '../styles/FileUpload.css';
import ReactMarkdown from 'react-markdown';

const FileUpload = () => {
  const [file, setFile] = useState(null);
  const [chatHistory, setChatHistory] = useState([]);
  const [question, setQuestion] = useState("");

  const askQuestion = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    setChatHistory(prev => [...prev, { role: 'user', content: question }]);
    setQuestion("");

    try {
      const res = await axios.post("http://localhost:8000/api/ask-question", {
        question,
      });
      setChatHistory(prev => [...prev, { role: 'bot', content: res.data.chat_response }]);
    } catch (err) {
      setChatHistory(prev => [...prev, { role: 'bot', content: "Sorry, there was an error processing your question." }]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await axios.post("http://localhost:8000/api/suggest-fields", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setChatHistory(prev => [...prev, { role: 'bot', content: res.data.chat_response }]);
    } catch (err) {
      setChatHistory(prev => [...prev, { role: 'bot', content: "Sorry, there was an error uploading your file." }]);
    }
  };

  return (
    <div className="form-bot">
      <h2>Upload Your Form</h2>
      <div className="chat-area">
        {[...chatHistory].reverse().map((msg, i) => (
          <div
            key={i}
            className={`chat-bubble ${msg.role === 'bot' ? 'bot-response' : 'user-message'}`}
          >
            <pre style={{ whiteSpace: "pre-wrap", fontFamily: "inherit" }}>
              <ReactMarkdown>{msg.content}</ReactMarkdown>
            </pre>
          </div>
        ))}
      </div>
      <input
        type="file"
        accept="image/*"
        onChange={(e) => setFile(e.target.files[0])}
      />
      <form onSubmit={askQuestion}>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question..."
        />
        <div className="button-container">
          <button type="button" onClick={handleUpload}>Upload & Ask</button>
          <button type="submit">Ask</button>
        </div>
      </form>
    </div>
  );
};

export default FileUpload;

