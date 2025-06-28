from fastapi import APIRouter, UploadFile, File
from app.services.ocr import extract_text_from_image
from fastapi import APIRouter, Query
from app.services.llm import get_matched_fields, generate_chat_response
from app.db.mongo import db
from fastapi.responses import JSONResponse

router = APIRouter()

@router.post("/suggest-fields")
async def suggest_fields(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        ocr_text = extract_text_from_image(contents)

        # Define known fields you expect
        known_fields = [
            "firstname", "lastname", "aadhaar_number", "pan_number","email_address",
            "phone_number", "gender", "address", "date_of_birth", "pincode", "city","state","country","annual_income",
            "marital_status"
        ]

        # Ask Gemini to match extracted text with known fields
        matched = get_matched_fields(ocr_text, known_fields)

        # Hardcode one user record for now
        user = await db["user_data"].find_one({"aadhaar_number": "1234-5678-9012"})
        user["_id"] = str(user["_id"])

        suggestions = {field: user[field] for field in matched if field in user}

        # New: Ask Gemini to explain suggestions in natural language
        chat_response = generate_chat_response(ocr_text, suggestions)

        return {
            "ocr_text": ocr_text,
            "matched_fields": matched,
            "suggestions": suggestions,
            "chat_response": chat_response
        }
    except Exception as e:
        print("🔥 Error in /suggest-fields:", e)
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@router.post("/extract-text")
async def extract_text(file: UploadFile = File(...)):
    contents = await file.read()
    text = extract_text_from_image(contents)
    print(text)
    return {"extracted_text": text}

@router.get("/get-user")
async def get_user_by_aadhaar(aadhaar: str = Query(...)):
    user = await db["user_data"].find_one({"aadhaar_number": aadhaar})
    if user:
        user["_id"] = str(user["_id"])  # convert ObjectId to string
    return user or {"message": "User not found"}