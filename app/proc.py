import ast
import datetime
import os
from io import BytesIO
from typing import Optional, Dict, Any

import pdfplumber
from PyPDF2 import PdfReader, PdfWriter
from pdf2image import convert_from_bytes
import requests
import re

from app import state
from forms.dagshub_ocr_old.form_ocr import process
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
os.environ['PATH'] = '/opt/homebrew/bin:' + os.environ['PATH']  # Only if needed




def res_dict_has_essentials(res_dict):
    return "042" in res_dict and "158" in res_dict and "244" in res_dict and "248" in res_dict and "045" in res_dict


def process_file_content( content: bytes, filename: str, form_name: str, category: str,
                         password: Optional[str] = "H6RH54",  use_local_extract = False) -> Dict[str, Any]:
    """Process the file content directly without saving to disk"""



    print(f"Processing file: {filename}")
    print(f"File size: {len(content)} bytes")
    print(f"Form name: {form_name}")
    print(f"Category: {category}")

    # Example processing based on file extension
    file_ext = filename.lower().split('.')[-1] if '.' in filename else ''

    if file_ext == 'pdf':

        def extract_text_method1(content, password):
            with pdfplumber.open(BytesIO(content), password=password) as pdf:
                #
                # attempt text analysis
                #

                all_text = ""
                for page in pdf.pages:
                    text = page.extract_text()
                    if text and text.strip():
                        all_text += text + "\n"
            return all_text

        def extract_text_method2(content, password):
            # attempt OCR 1
            # Process PDF with OCR 1
            images = convert_pdf_bytes_to_images(content, password)
            text = ""
            text = process(images, text)
            return text


        for method in [extract_text_method1, extract_text_method2]:
            try:
                state.init_results()

                text = method(content, password)
                if len(re.findall(r'[\u0590-\u05FF]{2,}', text)) < 10:
                    print(f"{method.__name__}: Less than 10 Hebrew words")
                    continue

                res_dict = look_for_codes(text, form_name, category, use_local_extract)

                if not res_dict_has_essentials(res_dict):
                    print(f"{method.__name__}: res_dict_has_essentials = False")
                    continue

                print(f"Success with {method.__name__}: {res_dict}")
                return {
                    "status": "Processed",
                    "file_type": file_ext,
                    "size": len(content),
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            except Exception as e:
                print(f"{method.__name__} failed: {e}")
                continue
        print("All methods failed.")
        # For other file types, skip OCR
        return {
            "status": "Skipped - Couldn't find known fields",
            "file_type": file_ext,
            "size": len(content),
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    elif file_ext in ['jpg', 'jpeg', 'png']:
        pass
    else:
        return {
            "status": "Skipped - Unsupported file type",
            "file_type": file_ext,
            "size": len(content),
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }


    """Process the file content directly without saving to disk"""


def look_for_codes(text, form_name, category, use_local_extract):
    if use_local_extract:
        return process_text_for_codes(text,
                                      state.PREDEFINED_CODES[form_name][category],
                                      state.PREDEFINED_CODES[form_name]["partner" if category=="main" else "main"] )
    return llm_process_text_for_codes(text,
                                  state.PREDEFINED_CODES[form_name][category],
                                  state.PREDEFINED_CODES[form_name]["partner" if category=="main" else "main"] )


def convert_pdf_bytes_to_images(pdf_bytes, password=None, save_dir="output_images"):
    if password is not None:
        reader = PdfReader(BytesIO(pdf_bytes))
        if reader.is_encrypted:
            if not reader.decrypt(password):
                raise ValueError("Incorrect password")
            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            output = BytesIO()
            writer.write(output)
            pdf_bytes = output.getvalue()
            output.close()

    # Convert decrypted PDF to images
    images = convert_from_bytes(pdf_bytes, dpi=800)

    # Ensure the output directory exists
    os.makedirs(save_dir, exist_ok=True)

    # Save each image to a file
    for idx, image in enumerate(images):
        image_path = os.path.join(save_dir, f"page_{idx + 1}.png")
        image.save(image_path, "PNG")

    return images


def process_text_for_codes(text, known_codes, partner_known_codes):
    # results is assumed to be initialized already
    # global results
    # Convert known_codes and partner_known_codes to integers for comparison
    known_codes_int = [int(code) for code in known_codes]
    partner_known_codes_int = [int(code) for code in partner_known_codes]

    results_dict = {}

    # Process each line separately
    for line in text.strip().split('\n'):
        # First, extract all numbers including those with thousand separators (e.g. "120,000")
        # We'll replace commas in numbers followed by 3 digits to handle thousand separators
        processed_line = re.sub(r'(\d+),(\d{3})', r'\1\2', line)

        # Store the original strings of numbers as they appear in the text
        number_matches = re.findall(r'\b\d+\b', processed_line)

        # Find all integers in the processed line
        integers = [int(num) for num in number_matches]

        # Keep track of the original string representation of each number
        number_strings = number_matches

        # Check each integer if it's a known code
        for i, num in enumerate(integers):
            if num in known_codes_int:
                # Check if there's a partner code (before or after the current code)
                partner_code = None
                sum_amount = None

                # Get the corresponding original code value for results dictionary
                code_index = known_codes_int.index(num)
                code_str = str(known_codes[code_index])  # Use string version as key

                # Check for partner code before the current code
                if i > 0 and integers[i - 1] in partner_known_codes_int:
                    # Check if they're actually coupled with a valid separator
                    # Use the original string representations for the regex pattern
                    # Valid separators: " ,", ", ", "/", "\", or enclosed in "[" and "]"
                    pattern = rf"{number_strings[i - 1]}(\s*,\s*|/|\\\\|\s*\[\s*|\s*\]\s*){number_strings[i]}"
                    if re.search(pattern, line):
                        partner_code = integers[i - 1]

                        # Look for sum before the partner code
                        if i > 1:
                            sum_amount = integers[i - 2]
                        # If no sum before partner, look after the main code
                        elif i < len(integers) - 1:
                            sum_amount = integers[i + 1]

                # Check for partner code after the current code
                elif i < len(integers) - 1 and integers[i + 1] in partner_known_codes_int:
                    # Check if they're actually coupled with a valid separator
                    # Use the original string representations for the regex pattern
                    # Valid separators: " ,", ", ", "/", "\", or enclosed in "[" and "]"
                    pattern = rf"{number_strings[i]}(\s*,\s*|/|\\\\|\s*\[\s*|\s*\]\s*){number_strings[i + 1]}"
                    if re.search(pattern, line):
                        partner_code = integers[i + 1]

                        # Look for sum before the main code
                        if i > 0:
                            sum_amount = integers[i - 1]
                        # If no sum before main code, look after partner code
                        elif i + 2 < len(integers):
                            sum_amount = integers[i + 2]

                # If no partner code, check for adjacent sum
                if partner_code is None:
                    # Look for sum before the code
                    if i > 0:
                        sum_amount = integers[i - 1]
                    # Look for sum after the code
                    elif i < len(integers) - 1:
                        sum_amount = integers[i + 1]

                # Update results if sum was found
                if sum_amount is not None:
                    results_dict[code_str] = sum_amount
                    state.results[code_str] += sum_amount

    print(f"Local Processing text results: {results_dict}")

    return results_dict


def llm_process_text_for_codes(text, known_codes, partner_known_codes):
    """
    Processes text to extract code-sum pairs using DeepSeek API.

    Args:
        text (str): The input text containing Hebrew lines with codes and sums
        known_codes (list): List of primary codes to extract
        partner_known_codes (list): List of secondary codes that might appear with primary codes

    Returns:
        dict: Mapping of code (str) to sum (int)
    """
    # Prepare the prompt
    prompt = f"""
    The following text contains Hebrew lines that start with code and end with sum.
    The code is one of the given known_codes: {known_codes} that may or may not be paired with one of partner_known_codes: {partner_known_codes}.
    Extract only the one that appears in known_codes.
    The code may appear surrounded by "[" or "]" in some order, may be separated from the other code by space or "," or "/" or "\\".
    The sum may be in a form like 10,000 or 10000. a code may apear twice, in which case you should sum the amounts for that code.
    Account also for reverse order, i.e., the code appearing last and sum first.

    Return ONLY a Python dictionary mapping code (as string) to sum (as int).
    Nothing else - just the dictionary.

    Here is the text to process:
    {text}
    """

    # Call DeepSeek API
    import os
    API_KEY = os.getenv("DEEPSEEK_API_KEY")
    API_URL = "https://api.deepseek.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1  # Lower temperature for more deterministic results
    }

    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        # Extract the dictionary from the response
        result_text = response.json()["choices"][0]["message"]["content"]

        # Safely evaluate the dictionary (caution with eval in production)
        # result_dict = eval(result_text)  #
        # result_dict = ast.literal_eval(result_text.lstrip("python").strip())
        result_dict = ast.literal_eval(result_text.strip().removeprefix("```python").removesuffix("```").strip())

        # Convert sums to integers (handle comma formatting)
        for code in result_dict:
            sum = result_dict[code]
            if isinstance(result_dict[code], str):
                sum = int(result_dict[code].replace(',', ''))
            state.results[code] += sum

        print(f"Llm Processing text results: {result_dict}")

        return result_dict


    except Exception as e:
        # yuvald TODO handle exception properly
        print(f"Error calling DeepSeek API: {e}")
        return False


