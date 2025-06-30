import re
import io
import numpy as np
from PIL import Image
import easyocr
from datetime import datetime

class DocumentExtractor:
    def __init__(self):
        self.reader = easyocr.Reader(['en', 'hi'], gpu=False)

    def _preprocess_image(self, image_bytes):
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        return img.point(lambda p: min(int(p * 1.5), 255))

    def _extract_text(self, image):
        result = self.reader.readtext(
            np.array(image),
            paragraph=False,
            detail=0,
            batch_size=4
        )
        return [line.strip() for line in result if line.strip()]

    def _clean_text(self, text):
        corrections = {
            'l': '1', '|': '1', 'I': '1', 'O': '0', 
            'B': '8', 'Z': '2', 'S': '5', '०': '0',
            '१': '1', '२': '2', '३': '3', '४': '4',
            '५': '5', '६': '6', '७': '7', '८': '8',
            '९': '9'
        }
        trans_table = str.maketrans(corrections)
        return text.translate(trans_table)

    # ================= AADHAAR EXTRACTION LOGIC =================
    def _is_likely_name(self, text):
        if not text or len(text.strip()) < 2 or len(text.strip()) > 40:
            return False
        if re.search(r'\d', text):
            return False
        keywords = [
            'GOVERNMENT', 'INDIA', 'DOB', 'BIRTH', 'MALE', 'FEMALE', 
            'ADDRESS', 'VID', 'VIRTUAL', 'जन्म', 'पुरुष', 'महिला',
            'AADHAAR', 'AADHAR', 'SCANNED BY', 'MERI PEHCHAN',
            'AUTHORITY', 'UNIQUE', 'IDENTIFICATION', 'COLLEGE', 'PATA', 'पता', 'पत्ताः'
        ]
        text_upper = text.upper()
        for kw in keywords:
            if kw in text_upper:
                return False
        if not re.search(r'[A-Za-z\u0900-\u097F]', text):
            return False
        words = text.split()
        if not (1 <= len(words) <= 4):
            return False
        return True

    def _extract_name_from_aadhaar(self, lines):
        header_keywords = [
            'भारत सरकार', 'GOVERNMENT OF INDIA', 'मारत सरकार', 'GOVERNMENT', 'सरकार'
        ]
        header_idx = -1
        for i, line in enumerate(lines):
            for kw in header_keywords:
                if kw in line.upper():
                    header_idx = i
                    break
            if header_idx != -1:
                break

        candidates = []
        for offset in range(1, 4):
            idx = header_idx + offset
            if 0 <= idx < len(lines):
                candidate = lines[idx].strip()
                if (
                    2 <= len(candidate) <= 30 and
                    not re.search(r'\d', candidate) and
                    not any(x in candidate.upper() for x in [
                        'DOB', 'BIRTH', 'MALE', 'FEMALE', 'ADDRESS',
                        'VID', 'VIRTUAL', 'SCANNED BY', 'AADHAAR', 'PEHCHAN',
                        'जन्म', 'महिला', 'पुरुष', 'पता', 'पत्ताः'
                    ])
                ):
                    candidates.append(candidate)
        for c in candidates:
            if re.search(r'[A-Za-z]', c):
                return c.title()
        for c in candidates:
            if re.search(r'[\u0900-\u097F]', c):
                return c
        for line in lines:
            line = line.strip()
            if (
                2 <= len(line) <= 30 and
                not re.search(r'\d', line) and
                not any(x in line.upper() for x in [
                    'DOB', 'BIRTH', 'MALE', 'FEMALE', 'ADDRESS',
                    'VID', 'VIRTUAL', 'SCANNED BY', 'AADHAAR', 'PEHCHAN',
                    'जन्म', 'महिला', 'पुरुष', 'पता', 'पत्ताः'
                ])
            ):
                if re.search(r'[A-Za-z]', line):
                    return line.title()
                elif re.search(r'[\u0900-\u097F]', line):
                    return line
        return None

    def _extract_address_aadhaar(self, lines, result):
        address_keywords = ['ADDRESS', 'पता', 'पत्ता']
        for i, line in enumerate(lines):
            for keyword in address_keywords:
                if keyword in line.upper():
                    address_lines = []
                    for j in range(i + 1, min(i + 4, len(lines))):
                        addr_line = lines[j].strip()
                        if (not re.search(r'\b[2-9][0-9]{3}\s?[0-9]{4}\s?[0-9]{4}\b', addr_line) and
                            'AADHAAR' not in addr_line.upper() and
                            'MERI PEHCHAN' not in addr_line.upper() and
                            len(addr_line) > 0):
                            address_lines.append(addr_line)
                    if address_lines:
                        result["address"] = ' '.join(address_lines)
                        return
        if len(lines) > 5:
            lower_section = lines[-5:]
            potential_address = []
            for line in lower_section:
                line = line.strip()
                if (line and 
                    not re.search(r'\b[2-9][0-9]{3}\s?[0-9]{4}\s?[0-9]{4}\b', line) and
                    'AADHAAR' not in line.upper() and
                    'MERI PEHCHAN' not in line.upper() and
                    'GOVERNMENT' not in line.upper() and
                    len(line) > 5):
                    potential_address.append(line)
            if potential_address:
                result["address"] = ' '.join(potential_address[:2])

    def _extract_aadhaar(self, lines):
        result = {}
        full_text = ' '.join(lines).upper()
        aadhaar_patterns = [
            r'\b[2-9][0-9]{3}\s?[0-9]{4}\s?[0-9]{4}\b',
            r'\b[2-9][0-9]{11}\b',
            r'\b[2-9][0-9]{3}-[0-9]{4}-[0-9]{4}\b'
        ]
        for pattern in aadhaar_patterns:
            match = re.search(pattern, full_text)
            if match:
                result["aadhaar_number"] = self._clean_text(match.group(0))
                break
        result["name"] = self._extract_name_from_aadhaar(lines)
        date_patterns = [
            r'\b(\d{2}/\d{2}/\d{4})\b',
            r'\b(\d{2}-\d{2}-\d{4})\b',
            r'\b(\d{2}\.\d{2}\.\d{4})\b'
        ]
        for pattern in date_patterns:
            match = re.search(pattern, full_text)
            if match:
                date_str = match.group(1)
                for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y']:
                    try:
                        datetime.strptime(date_str, fmt)
                        result["dob"] = date_str
                        break
                    except ValueError:
                        continue
                if "dob" in result:
                    break
        gender_keywords = {
            'MALE': ['MALE', 'M', 'पुरुष', 'पुरूष'],
            'FEMALE': ['FEMALE', 'F', 'महिला', 'स्त्री'],
            'TRANSGENDER': ['TRANSGENDER', 'T', 'ट्रांसजेंडर']
        }
        for line in lines:
            line_upper = line.upper()
            for gender, keywords in gender_keywords.items():
                if any(kw in line_upper for kw in keywords):
                    result["gender"] = gender
                    break
            if "gender" in result:
                break
        self._extract_address_aadhaar(lines, result)
        return result

    # ================= PAN EXTRACTION LOGIC =================
    def _extract_pan(self, lines):
        result = {}
        full_text = ' '.join(lines).upper()
        pan_pattern = r'\b([A-Z]{5}[0-9]{4}[A-Z]{1})\b'
        match = re.search(pan_pattern, full_text)
        if match:
            result["pan_number"] = match.group(1)
        else:
            for line in lines:
                match = re.search(pan_pattern, line.replace(" ", "").upper())
                if match:
                    result["pan_number"] = match.group(1)
                    break

        name, father_name = None, None

        # 1. Label-based extraction
        for i, line in enumerate(lines):
            if re.search(r'नाम\s*[/|:]|Name\s*[/|:]', line, re.IGNORECASE):
                for j in range(i+1, min(i+3, len(lines))):
                    if self._is_pan_name(lines[j]):
                        name = lines[j].strip().title()
                        break
            if re.search(r'पिता\s*का\s*नाम\s*[/|:]|Father\'?s?\s*Name\s*[/|:]', line, re.IGNORECASE):
                for j in range(i+1, min(i+3, len(lines))):
                    if self._is_pan_name(lines[j]):
                        father_name = lines[j].strip().title()
                        break

        # 2. Positional fallback
        if not name or not father_name:
            for i, line in enumerate(lines):
                if re.fullmatch(pan_pattern, line.replace(" ", "").upper()):
                    idx = i + 1
                    while idx < len(lines) and not name:
                        if self._is_pan_name(lines[idx]):
                            name = lines[idx].strip().title()
                            break
                        idx += 1
                    idx += 1
                    while idx < len(lines) and not father_name:
                        if self._is_pan_name(lines[idx]) and (lines[idx].strip().title() != name):
                            father_name = lines[idx].strip().title()
                            break
                        idx += 1
                    break

        # 3. First two unique names after PAN
        if not name or not father_name:
            pan_idx = -1
            for i, line in enumerate(lines):
                if re.fullmatch(pan_pattern, line.replace(" ", "").upper()):
                    pan_idx = i
                    break
            if pan_idx != -1:
                candidates = []
                for j in range(pan_idx+1, min(pan_idx+6, len(lines))):
                    val = lines[j].strip().title()
                    if self._is_pan_name(val) and val not in candidates:
                        candidates.append(val)
                if not name and len(candidates) > 0:
                    name = candidates[0]
                if not father_name and len(candidates) > 1:
                    father_name = candidates[1]

        # Prevent name = father_name
        if name and father_name and name == father_name:
            for line in lines:
                val = line.strip().title()
                if self._is_pan_name(val) and val != name:
                    father_name = val
                    break

        result["name"] = name
        result["father_name"] = father_name

        # Date of Birth
        dob = None
        dob_pattern = r'(\d{2}/\d{2}/\d{4})'
        for line in lines:
            match = re.search(dob_pattern, line)
            if match:
                try:
                    datetime.strptime(match.group(1), "%d/%m/%Y")
                    dob = match.group(1)
                    break
                except ValueError:
                    continue
        result["dob"] = dob

        return result

    def _is_pan_name(self, text):
        if not text or len(text.strip()) < 2 or len(text.strip()) > 40:
            return False
        if re.search(r'\d', text):
            return False
        keywords = [
            'INCOME TAX', 'DEPARTMENT', 'PERMANENT', 'ACCOUNT', 'NUMBER',
            'CARD', 'GOVT', 'INDIA', 'SIGNATURE', 'DATE', 'OF', 'BIRTH',
            'FATHER', 'NAME', 'पिता', 'नाम', 'हस्ताक्षर', 'जन्म', 'तिथि', 'कार्ड'
        ]
        text_upper = text.upper()
        for kw in keywords:
            if kw in text_upper:
                return False
        if not re.search(r'[A-Za-z]', text):
            return False
        return True

    # ================= MAIN EXTRACTION METHOD =================
    def extract_fields(self, image_bytes: bytes, doc_type: str) -> dict:
        image = self._preprocess_image(image_bytes)
        lines = self._extract_text(image)
        if doc_type == "aadhaar":
            result = self._extract_aadhaar(lines)
        elif doc_type == "pan":
            result = self._extract_pan(lines)
        else:
            raise ValueError("Unsupported document type")
        result["doc_type"] = doc_type
        return result

# Top-level function
def extract_fields(image_bytes: bytes, doc_type: str) -> dict:
    extractor = DocumentExtractor()
    return extractor.extract_fields(image_bytes, doc_type)
