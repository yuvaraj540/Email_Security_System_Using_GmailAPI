import os
import json
import subprocess
from flask import Flask, jsonify, request, render_template_string

app = Flask(__name__)

EMAILS_FILE = 'emails.json'
if os.path.exists(EMAILS_FILE):
    with open(EMAILS_FILE, 'r', encoding='utf-8') as f:
        try:
            emails = json.load(f)
        except json.JSONDecodeError:
            emails = []
else:
    emails = []

@app.route('/')
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Email Dashboard</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #1e1e2f;
                color: #f0f0f0;
            }
            .navbar {
                background-color: #333;
                overflow: hidden;
                padding: 14px 20px;
            }
            .navbar a {
                float: left;
                color: #f2f2f2;
                text-align: center;
                padding: 14px 16px;
                text-decoration: none;
                font-size: 17px;
            }
            .navbar a:hover {
                background-color: #ddd;
                color: black;
            }
            .navbar .brand {
                font-weight: bold;
                font-size: 20px;
            }
            .container {
                text-align: center;
                padding: 50px 20px;
            }
            #startBtn {
                font-size: 22px;
                padding: 14px 32px;
                cursor: pointer;
                background: linear-gradient(135deg, #ff6ec4, #7873f5);
                color: white;
                border: none;
                border-radius: 15px;
                position: relative;
                overflow: hidden;
                box-shadow: 0 0 15px #ff6ec4, 0 0 30px #7873f5;
                transition: all 0.4s ease-in-out;
                z-index: 1;
            }
            #startBtn:hover {
                transform: scale(1.1);
                box-shadow: 0 0 25px #ff6ec4, 0 0 50px #7873f5;
                background: linear-gradient(135deg, #ff8ef6, #5b5ce0);
            }
            #ratAnimation {
                display: none;
                margin-top: 30px;
            }
            #loadingText {
                margin-top: 15px;
                font-size: 18px;
            }
            #dashboard {
                display: none;
                padding: 40px;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
                table-layout: fixed;
                background-color: #2b2b3c;
                border-radius: 10px;
                overflow: hidden;
                border: 2px solid #444;
                transition: box-shadow 0.3s ease;
            }
            table:hover {
                box-shadow: 0 0 12px 2px #61dafb;
            }
            th, td {
                padding: 12px 16px;
                border: 1px solid #444;
                text-align: center;
                color: #e0e0e0;
                word-wrap: break-word;
                overflow: hidden;
                text-overflow: ellipsis;
                max-width: 152px;
            }
            th {
                background-color: #3a3a4f;
                font-weight: bold;
            }
            a {
                color: #61dafb;
            }

            /* From Uiverse.io by Nawsome */
            .wheel-and-hamster {
              --dur: 1s;
              position: relative;
              width: 12em;
              height: 12em;
              font-size: 14px;
              margin: 0 auto;
            }
            .wheel, .hamster, .hamster div, .spoke {
              position: absolute;
            }
            .wheel, .spoke {
              border-radius: 50%;
              top: 0;
              left: 0;
              width: 100%;
              height: 100%;
            }
            .wheel {
              background: radial-gradient(100% 100% at center, hsla(0,0%,60%,0) 47.8%, hsl(0,0%,60%) 48%);
              z-index: 2;
            }
            .spoke {
              background: repeating-conic-gradient(hsl(0, 0%, 60%) 0 1deg, transparent 1deg 30deg);
              z-index: 3;
            }
            .hamster {
              animation: hamster var(--dur) ease-in-out infinite;
              top: 50%;
              left: calc(50% - 3.5em);
              width: 7em;
              height: 3.75em;
              transform: rotate(4deg) translate(-0.8em, 1.85em);
              transform-origin: 50% 0;
              z-index: 1;
            }
            .hamster__head {
              animation: hamsterHead var(--dur) ease-in-out infinite;
              background: hsl(30,90%,55%);
              border-radius: 70% 30% 0 100% / 40% 25% 25% 60%;
              top: 0;
              left: -2em;
              width: 2.75em;
              height: 2.5em;
              transform-origin: 100% 50%;
            }
            .hamster__ear {
              animation: hamsterEar var(--dur) ease-in-out infinite;
              background: hsl(0,90%,85%);
              border-radius: 50%;
              top: -0.25em;
              right: -0.25em;
              width: 0.75em;
              height: 0.75em;
              transform-origin: 50% 75%;
            }
            .hamster__eye {
              animation: hamsterEye var(--dur) linear infinite;
              background-color: black;
              border-radius: 50%;
              top: 0.375em;
              left: 1.25em;
              width: 0.5em;
              height: 0.5em;
            }
            .hamster__nose {
              background: hsl(0,90%,75%);
              border-radius: 35% 65% 85% 15% / 70% 50% 50% 30%;
              top: 0.75em;
              left: 0;
              width: 0.2em;
              height: 0.25em;
            }
            .hamster__body {
              animation: hamsterBody var(--dur) ease-in-out infinite;
              background: hsl(30,90%,90%);
              border-radius: 50% 30% 50% 30% / 15% 60% 40% 40%;
              top: 0.25em;
              left: 2em;
              width: 4.5em;
              height: 3em;
              transform-origin: 17% 50%;
            }
            .hamster__limb--fr, .hamster__limb--fl {
              top: 2em;
              left: 0.5em;
              width: 1em;
              height: 1.5em;
              transform-origin: 50% 0;
            }
            .hamster__limb--br, .hamster__limb--bl {
              top: 1em;
              left: 2.8em;
              width: 1.5em;
              height: 2.5em;
              transform-origin: 50% 30%;
            }
            .hamster__tail {
              animation: hamsterTail var(--dur) linear infinite;
              background: hsl(0,90%,85%);
              border-radius: 0.25em 50% 50% 0.25em;
              top: 2.5em;
              left: -1em;
              width: 1em;
              height: 0.25em;
            }

            @keyframes hamster {
              0%, 100% { transform: rotate(4deg) translate(-0.8em, 1.85em); }
              50% { transform: rotate(0deg) translate(-0.8em, 1.85em); }
            }
            @keyframes hamsterHead {
              0%, 100% { transform: rotate(0); }
              50% { transform: rotate(-5deg); }
            }
            @keyframes hamsterEar {
              0%, 100% { transform: rotate(0); }
              50% { transform: rotate(10deg); }
            }
            @keyframes hamsterEye {
              0%, 90%, 100% { transform: scaleY(1); }
              95% { transform: scaleY(0.1); }
            }
            @keyframes hamsterBody {
              0%, 100% { transform: rotate(0); }
              50% { transform: rotate(2deg); }
            }
            @keyframes hamsterTail {
              0%, 100% { transform: rotate(0); }
              50% { transform: rotate(5deg); }
            }
            
            
            
            
            
            
            
            
            
            /* From Uiverse.io by Nawsome */ 
.wheel-and-hamster {
  --dur: 1s;
  position: relative;
  width: 12em;
  height: 12em;
  font-size: 14px;
}

.wheel,
.hamster,
.hamster div,
.spoke {
  position: absolute;
}

.wheel,
.spoke {
  border-radius: 50%;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.wheel {
  background: radial-gradient(100% 100% at center,hsla(0,0%,60%,0) 47.8%,hsl(0,0%,60%) 48%);
  z-index: 2;
}

.hamster {
  animation: hamster var(--dur) ease-in-out infinite;
  top: 50%;
  left: calc(50% - 3.5em);
  width: 7em;
  height: 3.75em;
  transform: rotate(4deg) translate(-0.8em,1.85em);
  transform-origin: 50% 0;
  z-index: 1;
}

.hamster__head {
  animation: hamsterHead var(--dur) ease-in-out infinite;
  background: hsl(30,90%,55%);
  border-radius: 70% 30% 0 100% / 40% 25% 25% 60%;
  box-shadow: 0 -0.25em 0 hsl(30,90%,80%) inset,
		0.75em -1.55em 0 hsl(30,90%,90%) inset;
  top: 0;
  left: -2em;
  width: 2.75em;
  height: 2.5em;
  transform-origin: 100% 50%;
}

.hamster__ear {
  animation: hamsterEar var(--dur) ease-in-out infinite;
  background: hsl(0,90%,85%);
  border-radius: 50%;
  box-shadow: -0.25em 0 hsl(30,90%,55%) inset;
  top: -0.25em;
  right: -0.25em;
  width: 0.75em;
  height: 0.75em;
  transform-origin: 50% 75%;
}

.hamster__eye {
  animation: hamsterEye var(--dur) linear infinite;
  background-color: hsl(0,0%,0%);
  border-radius: 50%;
  top: 0.375em;
  left: 1.25em;
  width: 0.5em;
  height: 0.5em;
}

.hamster__nose {
  background: hsl(0,90%,75%);
  border-radius: 35% 65% 85% 15% / 70% 50% 50% 30%;
  top: 0.75em;
  left: 0;
  width: 0.2em;
  height: 0.25em;
}

.hamster__body {
  animation: hamsterBody var(--dur) ease-in-out infinite;
  background: hsl(30,90%,90%);
  border-radius: 50% 30% 50% 30% / 15% 60% 40% 40%;
  box-shadow: 0.1em 0.75em 0 hsl(30,90%,55%) inset,
		0.15em -0.5em 0 hsl(30,90%,80%) inset;
  top: 0.25em;
  left: 2em;
  width: 4.5em;
  height: 3em;
  transform-origin: 17% 50%;
  transform-style: preserve-3d;
}

.hamster__limb--fr,
.hamster__limb--fl {
  clip-path: polygon(0 0,100% 0,70% 80%,60% 100%,0% 100%,40% 80%);
  top: 2em;
  left: 0.5em;
  width: 1em;
  height: 1.5em;
  transform-origin: 50% 0;
}

.hamster__limb--fr {
  animation: hamsterFRLimb var(--dur) linear infinite;
  background: linear-gradient(hsl(30,90%,80%) 80%,hsl(0,90%,75%) 80%);
  transform: rotate(15deg) translateZ(-1px);
}

.hamster__limb--fl {
  animation: hamsterFLLimb var(--dur) linear infinite;
  background: linear-gradient(hsl(30,90%,90%) 80%,hsl(0,90%,85%) 80%);
  transform: rotate(15deg);
}

.hamster__limb--br,
.hamster__limb--bl {
  border-radius: 0.75em 0.75em 0 0;
  clip-path: polygon(0 0,100% 0,100% 30%,70% 90%,70% 100%,30% 100%,40% 90%,0% 30%);
  top: 1em;
  left: 2.8em;
  width: 1.5em;
  height: 2.5em;
  transform-origin: 50% 30%;
}

.hamster__limb--br {
  animation: hamsterBRLimb var(--dur) linear infinite;
  background: linear-gradient(hsl(30,90%,80%) 90%,hsl(0,90%,75%) 90%);
  transform: rotate(-25deg) translateZ(-1px);
}

.hamster__limb--bl {
  animation: hamsterBLLimb var(--dur) linear infinite;
  background: linear-gradient(hsl(30,90%,90%) 90%,hsl(0,90%,85%) 90%);
  transform: rotate(-25deg);
}

.hamster__tail {
  animation: hamsterTail var(--dur) linear infinite;
  background: hsl(0,90%,85%);
  border-radius: 0.25em 50% 50% 0.25em;
  box-shadow: 0 -0.2em 0 hsl(0,90%,75%) inset;
  top: 1.5em;
  right: -0.5em;
  width: 1em;
  height: 0.5em;
  transform: rotate(30deg) translateZ(-1px);
  transform-origin: 0.25em 0.25em;
}

.spoke {
  animation: spoke var(--dur) linear infinite;
  background: radial-gradient(100% 100% at center,hsl(0,0%,60%) 4.8%,hsla(0,0%,60%,0) 5%),
		linear-gradient(hsla(0,0%,55%,0) 46.9%,hsl(0,0%,65%) 47% 52.9%,hsla(0,0%,65%,0) 53%) 50% 50% / 99% 99% no-repeat;
}

/* Animations */
@keyframes hamster {
  from, to {
    transform: rotate(4deg) translate(-0.8em,1.85em);
  }

  50% {
    transform: rotate(0) translate(-0.8em,1.85em);
  }
}

@keyframes hamsterHead {
  from, 25%, 50%, 75%, to {
    transform: rotate(0);
  }

  12.5%, 37.5%, 62.5%, 87.5% {
    transform: rotate(8deg);
  }
}

@keyframes hamsterEye {
  from, 90%, to {
    transform: scaleY(1);
  }

  95% {
    transform: scaleY(0);
  }
}

@keyframes hamsterEar {
  from, 25%, 50%, 75%, to {
    transform: rotate(0);
  }

  12.5%, 37.5%, 62.5%, 87.5% {
    transform: rotate(12deg);
  }
}

@keyframes hamsterBody {
  from, 25%, 50%, 75%, to {
    transform: rotate(0);
  }

  12.5%, 37.5%, 62.5%, 87.5% {
    transform: rotate(-2deg);
  }
}

@keyframes hamsterFRLimb {
  from, 25%, 50%, 75%, to {
    transform: rotate(50deg) translateZ(-1px);
  }

  12.5%, 37.5%, 62.5%, 87.5% {
    transform: rotate(-30deg) translateZ(-1px);
  }
}

@keyframes hamsterFLLimb {
  from, 25%, 50%, 75%, to {
    transform: rotate(-30deg);
  }

  12.5%, 37.5%, 62.5%, 87.5% {
    transform: rotate(50deg);
  }
}

@keyframes hamsterBRLimb {
  from, 25%, 50%, 75%, to {
    transform: rotate(-60deg) translateZ(-1px);
  }

  12.5%, 37.5%, 62.5%, 87.5% {
    transform: rotate(20deg) translateZ(-1px);
  }
}

@keyframes hamsterBLLimb {
  from, 25%, 50%, 75%, to {
    transform: rotate(20deg);
  }

  12.5%, 37.5%, 62.5%, 87.5% {
    transform: rotate(-60deg);
  }
}

@keyframes hamsterTail {
  from, 25%, 50%, 75%, to {
    transform: rotate(30deg) translateZ(-1px);
  }

  12.5%, 37.5%, 62.5%, 87.5% {
    transform: rotate(10deg) translateZ(-1px);
  }
}

@keyframes spoke {
  from {
    transform: rotate(0);
  }

  to {
    transform: rotate(-1turn);
  }
}
        </style>
    </head>
    <body>
        <div class="navbar">
            <a class="brand" href="#">📬 Email Dashboard</a>
            <a href="#">Home</a>
            <a href="#">About</a>
            <a href="#">Contact</a>
        </div>

        <div class="container">
            <h1>🚀 Welcome to Email Dashboard</h1>
            <button id="startBtn">✨ Start Server</button>

            <div id="ratAnimation">
                <!-- From Uiverse.io by Nawsome --> 
                <div aria-label="Orange and tan hamster running in a metal wheel" role="img" class="wheel-and-hamster">
                  <div class="wheel"></div>
                  <div class="hamster">
                    <div class="hamster__body">
                      <div class="hamster__head">
                        <div class="hamster__ear"></div>
                        <div class="hamster__eye"></div>
                        <div class="hamster__nose"></div>
                      </div>
                      <div class="hamster__limb hamster__limb--fr"></div>
                      <div class="hamster__limb hamster__limb--fl"></div>
                      <div class="hamster__limb hamster__limb--br"></div>
                      <div class="hamster__limb hamster__limb--bl"></div>
                      <div class="hamster__tail"></div>
                    </div>
                  </div>
                  <div class="spoke"></div>
                </div>
                <div id="loadingText">🐹 Server is running.....!</div>
            </div>
        </div>

        <div id="dashboard">
    <h2>📨 Emails</h2>
    <table>
        <thead>
            <tr>
                <th>From</th>
                <th>To</th>
                <th>Subject</th>
                <th>Attachment</th>
                <th>Attachment Conversion</th>
                <th>Attachment Link(s)</th>
                <th>Link</th>
                <th>Link Status</th>
            </tr>
        </thead>
        <tbody id="emailTableBody"></tbody>
    </table>
</div>

<script>
    document.getElementById('startBtn').addEventListener('click', function () {
        this.style.display = 'none';
        document.getElementById('ratAnimation').style.display = 'block';
        document.getElementById('dashboard').style.display = 'block';

        fetchEmails();
        setInterval(fetchEmails, 3000);
    });

    function fetchEmails() {
        fetch('/get_emails')
            .then(res => res.json())
            .then(data => {
                const tableBody = document.getElementById('emailTableBody');
                tableBody.innerHTML = '';
                data.forEach(email => {
                    let attachmentLinks = 'None';
                    if (email.attachment_conversion === 'SUCCESS' && email.attachment_location) {
                        attachmentLinks = email.attachment_location
                            .split(',')
                            .map(path => `<a href="javascript:void(0);" onclick="openFolder('${encodeURIComponent(path)}')">Open Folder</a>`)
                            .join('<br>');
                    }

                    const row = `
                        <tr>
                            <td>${email.from}</td>
                            <td>${email.to}</td>
                            <td>${email.subject}</td>
                            <td>${email.attachment}</td>
                            <td>${email.attachment_conversion}</td>
                            <td>${attachmentLinks}</td>
                            <td>${email.link ? `<a href="${email.link}" target="_blank">${email.link}</a>` : 'N/A'}</td>
                            <td>${email.url_status || 'unknown'}</td>
                        </tr>
                    `;
                    tableBody.innerHTML += row;
                });
            });
    }

    function openFolder(path) {
        fetch(`/open_folder?path=${encodeURIComponent(path)}`)
            .then(response => {
                if (response.ok) {
                    alert("Folder is opening...");
                } else {
                    alert("Error opening folder.");
                }
            })
            .catch(error => {
                alert("Error opening folder.");
            });
    }
</script>

    </body>
    </html>
    """)

@app.route('/get_emails')
def get_emails():
    return jsonify(emails)

@app.route('/receive_email', methods=['POST'])
def receive_email():
    data = request.json or {}
    emails.append({
        'from': data.get('from'),
        'to': data.get('to'),
        'subject': data.get('subject'),
        'attachment': data.get('attachment'),
        'attachment_conversion': data.get('attachment_conversion'),
        'attachment_location': data.get('attachment_location'),
        'link': data.get('link'),
        'url_status': data.get('url_status', 'unknown')
    })

    try:
        with open(EMAILS_FILE, 'w', encoding='utf-8') as f:
            json.dump(emails, f, indent=4, ensure_ascii=False)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'message': '✅ Email saved!'}), 200

@app.route('/open_folder')
def open_folder():
    path = request.args.get('path')
    if path and os.path.exists(path):
        try:
            subprocess.Popen([r'open_folder.bat', path])
            return jsonify({'message': 'Folder opened'})
        except Exception as e:
            return f"❌ Error opening folder: {str(e)}", 500
    return "❌ Invalid folder path", 404

if __name__ == '__main__':
    app.run(port=5000, debug=True)
