import pdfplumber
import pandas as pd
import re
from fastapi import HTTPException

def normalize_header(header: str) -> str:
    """
    Converts headers to SQL-safe column names.
    Example: "Amount (in Rs.)" -> "amount_in_rs"
    """
    if not header:
        return "unknown_col"
    # Remove special chars, replace spaces with _, lowercase
    clean = re.sub(r'[^a-zA-Z0-9\s]', '', str(header))
    clean = re.sub(r'\s+', '_', clean).lower()
    return clean[:60]  # Truncate to avoid DB limit issues

def extract_tables_from_pdf(file_path: str) -> list[dict]:
    """
    Extracts tables from all pages and returns a flat list of dicts.
    """
    extracted_data = []

    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                
                for table in tables:
                    # Logic: Identify header. We assume the row with the most text is the header
                    # or simply the first row. Here we take the first row.
                    if not table or len(table) < 2:
                        continue
                    
                    raw_headers = table[0]
                    # Handle None headers produced by pdfplumber for empty cells
                    raw_headers = [h if h is not None else f"col_{i}" for i, h in enumerate(raw_headers)]
                    
                    headers = [normalize_header(h) for h in raw_headers]
                    
                    # Process rows
                    for row in table[1:]:
                        # Skip empty rows
                        if not any(row):
                            continue
                            
                        # Normalize row length to match headers
                        row_data = [str(cell).replace('\n', ' ').strip() if cell else None for cell in row]
                        
                        # Pad or truncate row to match header length
                        if len(row_data) < len(headers):
                            row_data += [None] * (len(headers) - len(row_data))
                        else:
                            row_data = row_data[:len(headers)]
                            
                        record = dict(zip(headers, row_data))
                        extracted_data.append(record)
                        
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"PDF Parsing Failed: {str(e)}")

    return extracted_data