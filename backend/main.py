from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from PIL import Image
import pytesseract
from gtts import gTTS
import io
import requests

# Set path to Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))

    # OCR
    extracted_text = pytesseract.image_to_string(image)
    print("OCR Output:\n", extracted_text)

    # Get Hindi explanation using Groq
    explanation = explain_in_hindi_groq(extracted_text)
    print("Groq Explanation:\n", explanation)

    # Convert explanation to audio
    tts = gTTS(text=explanation, lang='hi')
    audio_path = "output.mp3"
    tts.save(audio_path)

    return {
        "message": "Success",
        "explanation": explanation,
        "audio_url": f"http://localhost:8000/audio/output.mp3"
    }

# Serve audio file
app.mount("/audio", StaticFiles(directory="."), name="audio")

# Function to explain document using Groq
GROQ_API_KEY = "your_groq_api_key_here"  # ⬅️ Replace with your actual key

def explain_in_hindi_groq(ocr_text):
    prompt = f"""
तुम एक सहायक हो जो बैंकिंग या दस्तावेज़ों की भाषा को सरल हिंदी में समझाता है। कृपया निम्नलिखित दस्तावेज़ को साधारण हिंदी में स्पष्ट करो ताकि एक सामान्य व्यक्ति भी समझ सके।

दस्तावेज़:
\"\"\"
{ocr_text}
\"\"\"

उत्तर (सरल हिंदी में):
"""
    headers = {
        "Authorization": f"Bearer {"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"}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.5,
        "max_tokens": 800
    }

    response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        print("Groq Error:", response.text)
        return "❌ Unable to explain the document."
