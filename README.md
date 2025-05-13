# 📧 Email Intelligence Dashboard

An end-to-end automated email processing system that:

- Pulls emails from Gmail
- Converts email attachments (PDFs, images) to previewable formats
- Extracts and scans URLs with an ML model
- Sends the results to a Flask dashboard for visualization

---

## 🚀 Features

- 📥 Gmail API integration for polling new emails
- 🖼️ Attachment conversion: PDF and images → standardized image format
- 🔍 ML-based malicious URL detection
- 🧠 Modular pipeline for scalable processing
- 📊 Interactive Flask dashboard with attachment previews and threat flags

---

## 📁 Project Structure

```
email-intelligence-dashboard/
│
├── poller/                    # Polls Gmail for new emails
│   └── poller.py
│
├── processor/                 # Handles attachments and ML checks
│   ├── attachment_handler.py
│   ├── url_checker.py
│   └── main.py
│
├── dashboard/                 # Flask dashboard
│   ├── app.py
│   ├── routes.py
│   └── templates/
│
├── static/                    # Static files (e.g., image previews)
│   └── images/
│
├── data/                      # Storage (e.g., SQLite DB)
│   └── db.sqlite
│
├── ml/                        # ML model
│   └── model.pkl
│
├── utils/
│   └── gmail_api.py           # Gmail token handling and utils
│
├── requirements.txt           # Python dependencies
└── README.md
```

---

## 🧰 Requirements

- Python 3.8+
- Gmail API access (OAuth2 credentials)
- Google Cloud Project (for Gmail API)
- ML model for URL analysis (e.g., sklearn, XGBoost, etc.)

---

## 📦 Installation

1. **Clone the Repository**

```bash
git clone https://github.com/yourusername/email-intelligence-dashboard.git
cd email-intelligence-dashboard
```

2. **Create and Activate a Virtual Environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**

```bash
pip install -r requirements.txt
```

4. **Set Up Gmail API Credentials**

- Follow [Gmail API Python Quickstart](https://developers.google.com/gmail/api/quickstart/python)
- Place `credentials.json` inside the root or `/utils` folder
- The app will generate a `token.json` on first run

---

## 🏃‍♂️ Running the Project

### 1. Start the Poller (to fetch new emails)

```bash
python poller/poller.py
```


### 2. Launch the Flask Dashboard

```bash
cd GUI
python app.py
```

Access the dashboard at [http://localhost:5000](http://localhost:5000)

---

## 🖼️ Dashboard Preview

- List of processed emails
- Sender, subject, timestamp
- URL analysis with "malicious" flags
- Attachment image previews

---

## ⚙️ Configuration Options

You can configure polling interval, allowed file types, and ML model path inside the relevant Python scripts (`poller.py`, `main.py`, etc.). Optional: convert these to a `.env` file or config JSON/YAML.

---

## 📌 Example Workflow

1. User sends an email with PDF/image attachments.
2. `poller.py` detects the email.
3. `main.py`:
   - Converts the attachments to PNG
   - Extracts and classifies URLs with an ML model
4. Processed data is sent to `Flask` backend.
5. The dashboard displays the results live.

---

## 🔐 Security Notes

- OAuth tokens are stored in `token.json`. Do **not** commit them.
- Validate inputs and sanitize all filenames/paths.
- ML model should be tested against adversarial attacks if used in production.

---

## 🧪 Testing

You can simulate email input using mock data or send test emails to the connected Gmail account.

Coming soon:
- Unit tests for attachment handling
- Test cases for ML model response

---

## 🧠 ML Model Notes

- Model format: `.pkl`
- Input: list of URLs
- Output: classification (e.g., 0 = safe, 1 = malicious)

Replace `url_checker.py` with your own logic if you use a different ML framework (TensorFlow, PyTorch, etc.)

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙋‍♂️ Contributions

PRs welcome! Please open an issue first for major changes. Follow the PEP8 style guide and write clean, modular code.
