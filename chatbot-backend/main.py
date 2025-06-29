import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# maps our front-end codes to prompt prefixes
PROMPT_PREFIX = {
    "hi": "साधारण हिंदी में उत्तर दें:",
    "en": "Answer in clear English:",
    "mr": "स्पष्ट मराठी मध्ये उत्तर द्या:",
    "ta": "சுருக்கமான தமிழில் பதில் வழங்கவும்:",
}

@app.post("/ask")
async def ask(request: Request):
    body = await request.json()
    user_input = body.get("message", "")
    lang = body.get("lang", "hi")

    # pick the right prefix (fallback to Hindi)
    prefix = PROMPT_PREFIX.get(lang, PROMPT_PREFIX["hi"])
    prompt = f"{prefix} {user_input}"

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return {"reply": response.text.strip()}
    except Exception as e:
        print("Error:", e)
        fallback = {
            "hi": "कुछ गलत हो गया है। कृपया पुनः प्रयास करें।",
            "en": "Something went wrong. Please try again.",
            "mr": "काही चुकलं, कृपया पुन्हा प्रयत्न करा.",
            "ta": "சேவை பிழை. தயவுசெய்து மீண்டும் முயற்சிக்கவும்."
        }
        return {"reply": fallback.get(lang, fallback["en"])}
