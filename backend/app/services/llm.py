from google import genai
from google.genai import types
import os
from app.core.config import settings
my_api_key = settings.GEMINI_API_KEY


client = genai.Client(api_key=my_api_key)

def get_matched_fields(ocr_text: str, known_fields: list[str]) -> list[str]:
    prompt = f"""
You are a form-filling assistant.

Below is the extracted text from a scanned form:

--- OCR TEXT START ---
{ocr_text}
--- OCR TEXT END ---

From the following known database fields:
{known_fields}

Return a Python list of field names that best match the information required in this form.
Some fields might be a combination of the known fields please include that in your decision like address might need address,city,state,pincode together.
Your response must be a plain Python list, e.g.: ['firstname', 'aadhaar_number', 'email_address']
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",  # or "gemini-2.5-flash" if you have access
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.4,
                top_p=1.0,
                top_k=40
            )
        )
        output = response.text.strip()

        # Safely evaluate the response
        fields = eval(output)
        if isinstance(fields, list):
            return fields
    except Exception as e:
        print("Gemini LLM error:", e)

    return []

def generate_chat_response(ocr_text: str, suggestions: dict) -> str:
    prompt = f"""
You are a helpful assistant that helps users fill scanned forms.

Here is the extracted text from a form:
--- OCR TEXT ---
{ocr_text}
--- END ---

You have matched these fields and their suggested values:
{suggestions}

Now explain to the user conversationally which fields were found and instruct them what to fill in the form.
Write clearly label : what to fill in the form.

For fields that could not be found please explain what each field and their options means and ask the user to fill it themselves.
Use a friendly tone. Respond in natural language (not code).
"""

    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.5,
                top_p=1.0,
            )
        )
        return response.text.strip()
    except Exception as e:
        print("Chat response error:", e)
        return "I found some fields you can fill. Please check the suggestions above."
