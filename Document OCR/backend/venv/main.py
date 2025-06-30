from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from ml.extractor import extract_fields
from pymongo import MongoClient
from fastapi.responses import JSONResponse

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

client = MongoClient("mongodb+srv://ruchif2005:VuNfxrLpmZTUQ3hx@cluster0.gpoos3j.mongodb.net/DocumentOCR?retryWrites=true&w=majority&appName=Cluster0")
db = client["user_data"]

collection = db["persons"]  # Central collection for merged records

@app.post("/upload")
async def upload(file: UploadFile = File(...), doc_type: str = Form(...)):
    contents = await file.read()
    fields = extract_fields(contents, doc_type)

    name = fields.get("name")
    if not name:
        return JSONResponse(content={"error": "Name not detected, cannot link documents."}, status_code=400)

    # Normalize name (case-insensitive match)
    query = {"name": {"$regex": f"^{name}$", "$options": "i"}}

    # Prepare fields to update
    update_fields = {}
    if doc_type == "aadhaar":
        for key in ["aadhaar_number", "dob", "gender"]:
            if key in fields:
                update_fields[key] = fields[key]
    elif doc_type == "pan":
        for key in ["pan_number", "father_name"]:
            if key in fields:
                update_fields[key] = fields[key]

    update_fields["doc_type_" + doc_type] = True  # Optional flag to track

    result = collection.update_one(query, {"$set": update_fields, "$setOnInsert": {"name": name}}, upsert=True)
    person_data = collection.find_one(query)

    # Convert _id to string for response
    person_data["_id"] = str(person_data["_id"])
    return JSONResponse(content=person_data)
