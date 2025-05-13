import os
import sys
import pickle
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from pptx import Presentation
from docx import Document
from pdf2image import convert_from_path
import requests

def make_safe_folder_name(sender_full_info):
    return (sender_full_info.replace('<', '')
                            .replace('>', '')
                            .replace('@', '_at_')
                            .replace('.', '_dot_')
                            .replace('"', '')
                            .replace(' ', '_')
                            .replace(':', '')
                            .replace('\\', '')
                            .replace('/', ''))

def text_to_image(text, width=800):
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()

    words = text.split()
    lines, line = [], ''
    for word in words:
        if len(line + ' ' + word) < 60:
            line += ' ' + word
        else:
            lines.append(line.strip())
            line = word
    if line:
        lines.append(line.strip())

    line_height = 20
    height = line_height * (len(lines) + 1)
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)

    y_text = 10
    for line in lines:
        draw.text((10, y_text), line, font=font, fill='black')
        y_text += line_height

    return image

def get_next_filename(folder, ext='png'):
    i = 1
    while True:
        filename = os.path.join(folder, f"{i}.{ext}")
        if not os.path.exists(filename):
            return filename
        i += 1

def convert_docx_to_image(docx_path):
    doc = Document(docx_path)
    text = '\n'.join([p.text for p in doc.paragraphs if p.text.strip()])
    return text_to_image(text)

def convert_excel_to_image(xlsx_path):
    df = pd.read_excel(xlsx_path)
    text = df.to_string(index=False)
    return text_to_image(text)

def convert_pdf_to_images(pdf_path):
    return convert_from_path(pdf_path, dpi=200)

def convert_ppt_to_images(ppt_path):
    print(f"[INFO] Converting {ppt_path} to PDF using LibreOffice...")
    abs_ppt_path = os.path.abspath(ppt_path)
    output_dir = os.path.dirname(abs_ppt_path)
    pdf_filename = os.path.splitext(os.path.basename(ppt_path))[0] + '.pdf'
    pdf_path = os.path.join(output_dir, pdf_filename)
    result = os.system(f'soffice --headless --convert-to pdf --outdir "{output_dir}" "{abs_ppt_path}" > nul 2>&1')
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"[ERROR] Expected PDF not found after conversion: {pdf_path}")
    return convert_pdf_to_images(pdf_path)

def convert_to_image(file_path):
    ext = file_path.lower().split('.')[-1]
    if ext in ['png', 'jpg', 'jpeg', 'bmp', 'gif']:
        return [Image.open(file_path)]
    elif ext in ['docx', 'doc']:
        return [convert_docx_to_image(file_path)]
    elif ext in ['pptx', 'ppt']:
        return convert_ppt_to_images(file_path)
    elif ext in ['xlsx', 'xls']:
        return [convert_excel_to_image(file_path)]
    elif ext in ['txt', 'py', 'csv']:
        with open(file_path, 'r', errors='ignore') as f:
            text = f.read(2000)
        return [text_to_image(text)]
    elif ext == 'pdf':
        return convert_pdf_to_images(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_path}")

def check_url(url):
    whitelist = ['hackthebox.eu', 'root-me.org', 'gmail.com']
    if url in whitelist:
        return 'good'
    try:
        with open('Features/new_model.pkl', 'rb') as f1:
            model = pickle.load(f1)
        with open('Features/new_vectorizer.pkl', 'rb') as f2:
            vectorizer = pickle.load(f2)
        x = vectorizer.transform([url])
        prediction = model.predict(x)
        return prediction[0]
    except Exception as e:
        with open('error_log.txt', 'a') as log_file:
            log_file.write(f"Error while checking URL '{url}': {str(e)}\n")
        return 'unknown'

# ---------------- Main Logic ----------------
if __name__ == '__main__':
    if len(sys.argv) < 6:
        print("Usage: python main.py <file1,file2,...> <sender_email> <receiver_email> <subject> <url>")
        sys.exit(1)

    file_list_raw = sys.argv[1]
    sender_email = sys.argv[2]
    receiver_email = sys.argv[3]
    subject = sys.argv[4]
    links = sys.argv[5]

    file_paths = file_list_raw.split(',') if file_list_raw.lower() != "none" else []

    print("═" * 70)
    print("📬 Email Processing Started")
    print(f"From       : {sender_email}")
    print(f"To         : {receiver_email}")
    print(f"Subject    : {subject}")
    print(f"Attachments: {file_paths if file_paths else 'None'}")
    print(f"Links      : {links if links.lower() != 'none' else 'None'}")
    print("═" * 70)

    attachment_names = []
    saved_image_paths = []
    attachment_conversion_success = False
    attachment_folder = "None"

    root_folder = "Processed_Attachments"
    os.makedirs(root_folder, exist_ok=True)

    if file_paths:
        try:
            folder_name = make_safe_folder_name(sender_email + "_" + receiver_email + "_" + subject)
            folder_name = os.path.join(root_folder, folder_name)
            os.makedirs(folder_name, exist_ok=True)
            attachment_folder = folder_name

            for path in file_paths:
                if not os.path.exists(path):
                    print(f"[WARNING] File not found: {path}")
                    continue
                images = convert_to_image(path)
                for img in images:
                    image_path = get_next_filename(folder_name)
                    img.save(image_path)
                    saved_image_paths.append(image_path)
                attachment_names.append(os.path.basename(path))

            if saved_image_paths:
                attachment_conversion_success = True

        except Exception as e:
            print(f"[ERROR] Failed to process attachments: {e}")
            attachment_conversion_success = False

    url_result = "unknown"
    if links.lower() != "none" and links.strip():
        try:
            url_result = check_url(links)
        except Exception as e:
            print(f"[ERROR] Failed to check URL: {e}")
            url_result = "unknown"

    # # 🧾 Log when both attachment and link are missing
    # if not file_paths and (links.lower() == "none" or not links.strip()):
    #     print("─────────────────────────────────────────────────────")
    #     print(f"📭 No attachment and no URL found for email from {sender_email} to {receiver_email} regarding '{subject}'.")
    #     print("─────────────────────────────────────────────────────")

    # 🚀 Always send payload to Flask backend
    payload = {
        "from": sender_email,
        "to": receiver_email,
        "subject": subject,
        "attachment": ', '.join(attachment_names) if attachment_names else "None",
        "attachment_conversion": "SUCCESS" if attachment_conversion_success else "NO",
        "attachment_location": attachment_folder,
        "link": links,
        "url_status": url_result
    }

    try:
        response = requests.post("http://127.0.0.1:5000/receive_email", json=payload)
        print(f"[✅] Payload sent to Flask: {response.json()}")
    except Exception as e:
        print(f"[ERROR] Could not send to Flask server: {e}")

    print("═" * 70)
    print("✅ Email processing completed.")
    print("═" * 70)
