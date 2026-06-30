import re
import os
from datetime import datetime

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


def extract_text_from_pdf(file_path, password=None):
    if not PDF_AVAILABLE:
        return None, 'PyPDF2 not available'
    try:
        text = ''
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            # Try to decrypt if password is provided
            if reader.is_encrypted:
                if not password or password.strip() == '':
                    return None, 'PDF is password-protected. Please provide the password.'
                try:
                    # Try both user password and owner password
                    decrypted = reader.decrypt(password)
                    if not decrypted:
                        return None, 'Incorrect PDF password. Please try again.'
                except Exception as e:
                    return None, f'Failed to decrypt PDF: {str(e)}'
            for page in reader.pages:
                text += page.extract_text() or ''
        if not text or text.strip() == '':
            return None, 'Could not extract text from PDF. The file may be empty or image-based.'
        return text, None
    except Exception as e:
        return None, f'Error reading PDF: {str(e)}'


def parse_transactions_from_text(text):
    transactions = []
    lines = text.split('\n')
    debit_total = 0
    credit_total = 0

    amount_pattern = re.compile(r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)')
    date_pattern = re.compile(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{2}\s+\w{3}\s+\d{4})')

    for line in lines:
        if len(line.strip()) < 5:
            continue
        date_match = date_pattern.search(line)
        amounts = amount_pattern.findall(line)
        if date_match and amounts:
            line_lower = line.lower()
            is_debit = any(k in line_lower for k in ['dr', 'debit', 'withdrawal', 'paid', 'purchase'])
            is_credit = any(k in line_lower for k in ['cr', 'credit', 'deposit', 'received', 'salary'])
            for amt_str in amounts:
                try:
                    amt = float(amt_str.replace(',', ''))
                    if amt > 0:
                        txn_type = 'debit' if is_debit else ('credit' if is_credit else 'unknown')
                        transactions.append({
                            'date': date_match.group(1),
                            'description': line.strip()[:100],
                            'amount': amt,
                            'type': txn_type,
                        })
                        if txn_type == 'debit':
                            debit_total += amt
                        elif txn_type == 'credit':
                            credit_total += amt
                        break
                except ValueError:
                    pass

    return {
        'transactions': transactions[:100],
        'summary': {
            'total_debits': round(debit_total, 2),
            'total_credits': round(credit_total, 2),
            'net': round(credit_total - debit_total, 2),
            'transaction_count': len(transactions),
        }
    }


def parse_csv_statement(file_path):
    if not PANDAS_AVAILABLE:
        return None, 'Pandas not available'
    try:
        df = pd.read_csv(file_path)
        transactions = []
        debit_total = 0
        credit_total = 0

        col_map = {}
        for col in df.columns:
            col_lower = col.lower().strip()
            if 'date' in col_lower:
                col_map['date'] = col
            elif 'desc' in col_lower or 'narration' in col_lower or 'particular' in col_lower:
                col_map['description'] = col
            elif 'debit' in col_lower or 'withdrawal' in col_lower:
                col_map['debit'] = col
            elif 'credit' in col_lower or 'deposit' in col_lower:
                col_map['credit'] = col
            elif 'amount' in col_lower:
                col_map['amount'] = col

        for _, row in df.iterrows():
            txn = {
                'date': str(row.get(col_map.get('date', ''), '')),
                'description': str(row.get(col_map.get('description', ''), ''))[:100],
                'amount': 0,
                'type': 'unknown',
            }
            if col_map.get('debit'):
                try:
                    d = float(str(row[col_map['debit']]).replace(',', '').replace('₹', ''))
                    if d > 0:
                        txn['amount'] = d
                        txn['type'] = 'debit'
                        debit_total += d
                except (ValueError, TypeError):
                    pass
            if col_map.get('credit'):
                try:
                    c = float(str(row[col_map['credit']]).replace(',', '').replace('₹', ''))
                    if c > 0 and txn['type'] == 'unknown':
                        txn['amount'] = c
                        txn['type'] = 'credit'
                        credit_total += c
                except (ValueError, TypeError):
                    pass
            if txn['amount'] > 0:
                transactions.append(txn)

        return {
            'transactions': transactions,
            'summary': {
                'total_debits': round(debit_total, 2),
                'total_credits': round(credit_total, 2),
                'net': round(credit_total - debit_total, 2),
                'transaction_count': len(transactions),
            }
        }, None
    except Exception as e:
        return None, str(e)


def auto_categorize_transaction(description):
    desc_lower = description.lower()
    categories = {
        'Food & Dining': ['swiggy', 'zomato', 'restaurant', 'cafe', 'food', 'pizza', 'burger', 'biryani', 'hotel'],
        'Transportation': ['uber', 'ola', 'fuel', 'petrol', 'diesel', 'irctc', 'railway', 'metro', 'bus'],
        'Shopping': ['amazon', 'flipkart', 'myntra', 'shopping', 'mall', 'store'],
        'Bills & Utilities': ['electricity', 'bses', 'tata power', 'water', 'gas', 'broadband', 'airtel', 'jio', 'vi '],
        'Entertainment': ['netflix', 'amazon prime', 'spotify', 'hotstar', 'disney', 'cinema', 'bookmyshow'],
        'Healthcare': ['pharmacy', 'medical', 'hospital', 'apollo', 'doctor', 'clinic', 'medicine'],
        'Groceries': ['dmart', 'bigbasket', 'grofers', 'blinkit', 'zepto', 'grocery', 'vegetable'],
        'Education': ['course', 'udemy', 'coursera', 'school', 'college', 'fees', 'tuition'],
        'Rent & Housing': ['rent', 'housing', 'maintenance', 'society'],
        'Investments': ['mutual fund', 'sip', 'zerodha', 'groww', 'stock', 'demat'],
    }
    for category, keywords in categories.items():
        if any(kw in desc_lower for kw in keywords):
            return category
    return 'Others'
