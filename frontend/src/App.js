// src/App.js
import React from 'react';
import Chatbot from "./components/Chatbot.jsx";
import DocumentExplainer from './pages/DocumentExplainer.js'; // Adjust the path as necessary
import FileUpload from './pages/FileUpload.jsx';

function App() {
  return (
<>
    <Chatbot />
    <DocumentExplainer />
    <FileUpload />
</>
  )
}

export default App;
