import json
import re
from collections import defaultdict

import re
from collections import defaultdict

import re
from collections import defaultdict

import re

import re

from collections import defaultdict

import re
from collections import defaultdict


def extract_form_data(html_content):
    result = defaultdict(lambda: {"main": [], "partner": []})

    # Split the content on KodXXX occurrences
    sections = re.split(r'id="Kod(\d+)"', html_content)

    # Ignore the first section (before first KodXXX)
    for i in range(1, len(sections), 2):
        code = sections[i]  # The captured KodXXX number
        section_content = sections[i + 1]  # Everything after this KodXXX

        # Find TofesYYY in this section
        form_match = re.search(r'Tofes(\d+)', section_content)
        if not form_match:
            continue

        form = form_match.group(1)

        # Check for both classifications
        is_main = "BenZugRashum" in section_content
        is_partner = "שאינו" in section_content

        # Apply classification rules
        if is_main and is_partner:
            result[form]["main"].append(code)
            result[form]["partner"].append(code)
        elif is_main:
            result[form]["main"].append(code)
        elif is_partner:
            result[form]["partner"].append(code)
        else:  # If neither appears
            result[form]["main"].append(code)

    # Convert defaultdict to regular dict and sort codes
    final_result = {}
    for form in result:
        final_result[form] = {
            "main": sorted(result[form]["main"]),
            "partner": sorted(result[form]["partner"])
        }

    return final_result

# Example usage:
# with open('your_file.html', 'r', encoding='utf-8') as file:
#     html_content = file.read()
#
# extracted_data = extract_form_data(html_content)
# print(extracted_data)


# Example usage:
# with open('your_file.html', 'r', encoding='utf-8') as file:
#     html_content = file.read()
#
# extracted_data = extract_form_data(html_content)
# print(extracted_data)


if __name__ == "__main__":
    try:
        # Process the file
        with open('explainer-full.html', 'r', encoding='utf-8') as file:
            html_content = file.read()

        result = extract_form_data(html_content)
        print(result)
        # Print the result as indented JSON
        print(json.dumps(result, ensure_ascii=False, indent=2))

    except FileNotFoundError:
        print("File 'explainer-full.html' not found. Please ensure the file is in the same directory.")
    except Exception as e:
        print(f"An error occurred: {e}")

