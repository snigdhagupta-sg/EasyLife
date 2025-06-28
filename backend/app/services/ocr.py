import pytesseract
import cv2
import numpy as np

def extract_text_from_image(image_bytes: bytes) -> str:
    # Convert bytes to OpenCV image
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Use Tesseract OCR
    text = pytesseract.image_to_string(img)
    return text.strip()
