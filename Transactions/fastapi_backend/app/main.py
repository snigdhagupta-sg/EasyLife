import jwt
from fastapi import Request, HTTPException
from fastapi import FastAPI, File, UploadFile
from fastapi import APIRouter, HTTPException
from fastapi import Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import pytesseract
import cv2
import numpy as np
import re
from bson import ObjectId
from pymongo import MongoClient
from fastapi.responses import JSONResponse
app = FastAPI()
from dotenv import load_dotenv
from google import genai
import os
import json
load_dotenv()

client = genai.Client(api_key = os.getenv("GENAI_API_KEY"))
mongo_client = MongoClient(os.getenv("MONGODB_URL"))

db = mongo_client[os.getenv("MONGODB_DB_NAME")]
accounts_col = db["accountnumbers"]
transactions_col = db["transactions"]

from pydantic import BaseModel
from typing import Optional

class Transaction(BaseModel):
    account_number: Optional[str] = None
    credited_debited: Optional[str] = None
    amount: Optional[float] = 0.0
    date: Optional[str] = None
    reference_number: Optional[str] = None
    to_from: Optional[str] = None


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def preprocess_image(image_bytes: bytes) -> np.ndarray:
    # Convert bytes to numpy array
    np_arr = np.frombuffer(image_bytes, np.uint8)
    # Decode image from numpy array
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Failed to decode image from bytes.")   
    # Resize, grayscale, etc. if needed
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray

def extract_text_from_image(image_path):
    preprocessed_image = preprocess_image(image_path)   
    # Use Tesseract to extract text
    extracted_text = pytesseract.image_to_string(preprocessed_image)
    return extracted_text

def return_transactions(text: str) -> dict:
    prompt = (
        f"""I will provide you with text extracted from bank transaction messages. Your task is to parse this text and return an array of JSON objects. Each JSON object should represent a single transaction and contain the following keys with their corresponding values:

account_number: The last four digits of the account number (e.g., X1815 should become 1815).
credited_debited: Indicate whether the account was "credited" or "debited."
amount: The transaction amount as a float (e.g., 20.0, 150.0).
date: The date of the transaction in DD/MM/YY format. For example, if the text states 03Apr25, the date should be 03/04/25. Please convert the month abbreviation (e.g., Apr, Jun) to its corresponding two-digit number.
to_from: The name of the recipient (for 'debited' transactions, usually after 'trf to') or sender (for 'credited' transactions, usually after 'transfer from').
reference_number: The transaction reference number.

Please extract this information for every transaction present in the text and ensure the output is a single JSON array containing all the transaction objects.

Here is the text:
{text}
"""
    )

    print("✅ Gemini prompt:\n", prompt)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )

    print("✅ Gemini response:\n", response.text)

    return response.text


class Message(BaseModel):
    user_input: str

@app.post("/chat")
async def chat(message: Message):
    user_text = message.user_input
    prompt = (
        "Be the friendliest chat bot and respond to the customers query but keep in mind to give a concise answer. \n"
        "Give a short summary answer."
        f"Prescription Text:\n{user_text}"
    )
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    reply_text = response.text 
    return {"reply": reply_text}

@app.post("/extract_text/")
async def extract_text(file: UploadFile = File(...)):
    contents = await file.read()
    raw_text = extract_text_from_image(contents)
    print(raw_text)
    return {"extracted_text": raw_text}


@app.post("/return_transactions/")
async def return_transactions_from_raw_text(data: dict):
    text = data.get("text", "")
    response_text = return_transactions(text)
    return response_text


from typing import List

from typing import List

@app.post("/upload_transactions/")
async def upload_transactions(request: Request, data: List[Transaction]):
    JWT_SECRET = os.getenv("JWT_SECRET")

    user_id = request.cookies.get("user_id")

    if not user_id:
        raise HTTPException(status_code=401, detail="User not logged in")

    inserted = []
    i = 0
    for item in data:
        item = item.dict()  # convert from Pydantic model to dict
        print(i)
        i = i + 1
        required_keys = {"account_number", "credited_debited", "amount", "date", "reference_number"}
        if any(key not in item or item[key] in [None, ""] for key in required_keys):
            print("All required keys not present")
            continue

        if transactions_col.find_one({"reference_number": item["reference_number"]}):
            print("Reference number already present")
            continue

        suffix = item["account_number"]
        full_account = accounts_col.find_one({"account_number": {"$regex": f"{suffix}$"}})
        if not full_account:
            print("Account number not present")
            continue

        item["account_number"] = full_account["account_number"]
        item["user_id"] = user_id
        transactions_col.insert_one(item)
        inserted.append(item)
        print("Inserted")

        
    for item in inserted:
        item.pop("_id", None)
    return {"inserted_count": len(inserted), "inserted_transactions": inserted}
