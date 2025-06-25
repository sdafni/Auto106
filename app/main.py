from fastapi import FastAPI, Request, File, UploadFile, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uuid
from typing import Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time
import os

from app import state
from app.proc import process_file_content

os.environ['PATH'] = '/opt/homebrew/bin:' + os.environ['PATH']  # Only if needed

# Create application
app = FastAPI()

# TODOs
# support different file types
# notify on no change in inputs
# reset button (a refresh currently)
# avoid dup files
# gray button when no file loaded
# user session results etc, ask fastapi
# have user select simulator or report
# progress indicator
# ui report on whats found
# choose sim or tax report
# add delete option, requires db/mem-db
# filter out 1 shekel
# better do the fallback of options (re-search code concept)

# Set up static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")



@app.get("/", response_class=HTMLResponse)
async def index(request: Request):

    """Render the main page with file upload form"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload-file/", response_class=HTMLResponse)
async def upload_file(
        request: Request,
        file: UploadFile = File(...),
        form_name: str = Form(...),
        category: str = Form(...),
        password: Optional[str] = Form(None, alias="pdf_password"),
        use_local_extract: bool = Form(False)

):
    """Process file upload and return HTML for the new file row"""

    # Generate a unique ID for this upload
    file_id = str(uuid.uuid4())

    # Read the file content
    content = await file.read()

    # Process the file content directly (no saving to disk)
    result = process_file_content( content, file.filename, form_name, category, password, use_local_extract = use_local_extract)

    # Get status message based on processing result
    status = result.get("status", "Processed")
    status_class = "bg-green-100 text-green-800" if status == "Processed" else "bg-blue-100 text-blue-800"

    # Generate HTML for the stats table
    stats_html = generate_stats_html()
    password_used = "כן" if password else "לא"
    category = "עיקרי" if category == "main" else "השני"
    # Return combined HTML fragments
    return f"""
    <tr id="file-{file_id}" class="border-b hover:bg-gray-50">
        <td class="py-2 px-4 text-sm">{file.filename}</td>
        <td class="py-2 px-4 text-sm">{form_name}</td>
        <td class="py-2 px-4 text-sm">{category}</td>
        <td class="py-2 px-4 text-sm">{password_used}</td>
    </tr>
    <script>
        document.getElementById('stats-container').innerHTML = `{stats_html}`;
    </script>
    """

@app.post("/auto-fill/")
async def trigger_auto_fill():
    try:
        auto_fill()
        return {"status": "success", "message": "Browser opened and form filled"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def auto_fill():
    # Start WebDriver
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 15)

    try:
        # Step 1: Go to main.aspx
        driver.get("https://secapp.taxes.gov.il/shSimulatorMas/main.aspx")

        # Step 2: Wait for year dropdown to load and select 2022
        year_select = wait.until(EC.presence_of_element_located((By.ID, "ddlYears")))
        Select(year_select).select_by_visible_text("2022")

        # Step 3: Wait for redirect to DochSchirim22.aspx
        wait.until(EC.url_contains("DochSchirim22.aspx"))

        # Step 4: Wait for table with inputs to load
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))

        # Step 5: Fill in the input fields
        for field_id, value in state.results.items():
            if value == 0:
                continue
            try:
                input_elem = driver.find_element(By.XPATH, f"//input[contains(@id, '{field_id}')]")
                input_elem.clear()
                input_elem.send_keys(value)
                print(f"Filled {field_id} with {value}")

                # Optional: short wait for validation to trigger
                time.sleep(0.3)

                # Optional: validate related div exists
                valid_div_id = f"valid{field_id}"
                try:
                    valid_div = driver.find_element(By.ID, valid_div_id)
                    print(f"Validation div for {field_id}: {valid_div.text.strip()}")
                except:
                    print(f"No validation div found for {field_id}")

            except Exception as e:
                print(f"Failed to fill field {field_id}: {e}")

        print("Browser window is open and ready for user interaction.")
        # Don't close the browser, let it stay open for user interaction
        return

    except Exception as e:
        print(f"An error occurred: {e}")
        driver.quit()
        raise e


def generate_stats_html() -> str:
    html = '<table>'
    for code, count in state.results.items():
        if count > 0:
            html += f'        <tr>\n            <td>{code}</td>\n            <td>{count}</td>\n        </tr>\n'
    html += '</table>'
    return html


if __name__ == "__main__":
    if not os.environ.get("IS_RENDER"):
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)