import os
import re
from datetime import datetime

try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False


def extract_text_from_image(image_path):
    if not OCR_AVAILABLE:
        return None, 'OCR not available'
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text, None
    except Exception as e:
        return None, str(e)


def parse_receipt(text):
    result = {
        'amount': None,
        'date': None,
        'title': None,
        'category': 'Others',
        'raw_text': text,
    }
    amount_patterns = [
        r'(?:total|amount|grand total|net amount)[:\s]*(?:rs\.?|inr|₹)?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
        r'(?:rs\.?|inr|₹)\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
        r'(\d+(?:,\d+)*(?:\.\d{2})?)\s*(?:rs\.?|inr|₹)',
    ]
    for pattern in amount_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            amount_str = match.group(1).replace(',', '')
            try:
                result['amount'] = float(amount_str)
                break
            except ValueError:
                pass

    date_patterns = [
        r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'(\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{2,4})',
    ]
    for pattern in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            result['date'] = match.group(1)
            break

    lines = [l.strip() for l in text.split('\n') if l.strip() and len(l.strip()) > 3]
    if lines:
        result['title'] = lines[0][:100]

    category_keywords = {
        'Food & Dining': ['restaurant', 'cafe', 'food', 'hotel', 'pizza', 'burger', 'zomato', 'swiggy', 'biryani'],
        'Shopping': ['shopping', 'mall', 'store', 'mart', 'amazon', 'flipkart', 'myntra'],
        'Transportation': ['fuel', 'petrol', 'diesel', 'cab', 'uber', 'ola', 'auto', 'bus', 'train'],
        'Healthcare': ['pharmacy', 'medical', 'hospital', 'clinic', 'medicine', 'doctor'],
        'Bills & Utilities': ['electric', 'water', 'gas', 'internet', 'phone', 'mobile', 'bill'],
        'Entertainment': ['cinema', 'movie', 'theatre', 'netflix', 'spotify'],
        'Groceries': ['grocery', 'supermarket', 'vegetables', 'fruits', 'milk'],
    }
    text_lower = text.lower()
    for category, keywords in category_keywords.items():
        if any(kw in text_lower for kw in keywords):
            result['category'] = category
            break

    return result


def process_receipt_image(image_path):
    text, err = extract_text_from_image(image_path)
    if err:
        return None, err
    parsed = parse_receipt(text)
    return parsed, None
