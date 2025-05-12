# secured_ftp

# 🔐 Secure FTP Server

A multi-client, secure FTP server implemented in Python using low-level TCP sockets and the `select()` system call.  
This project was developed as part of the Computer and Network Security course at SIIT – Thammasat University.

## 🧩 Features

- ✅ Multi-client support using `select()`
- 🔐 Secure login with SHA-256 password hashing
- 👤 Role-based access (User / Admin)
- 📁 Isolated directory per user (sandbox)
- 🚫 Brute-force login detection and blocking
- 🕵️ Honeypot for suspicious usernames (e.g., `root`, `admin123`)
- 📜 Logging of all actions and intrusions

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/nourrysebastieN/secured_ftp.git
cd secured_ftp
```

### 2. Create the users.json file
```bash
{
  "alice": {
    "password": "<SHA256_HASH>",
    "role": "user"
  },
  "admin": {
    "password": "<SHA256_HASH>",
    "role": "admin"
  }
}

```

Generate the SHA256 hash of the password using the following command:
```bash
echo -n "your_password" | sha256sum
```

### 3. Run the server
```bash
python ftp_server.py
# or
chmod +x ftp_server.py
./ftp_server.py
```

### 4. Connect to the server
You can use the client provided to launch connect to the Ftp server
```bash
python ftp_client.py --port <port> --host <host>
# or
chmod +x ftp_client.py
./ftp_client.py --port <port> --host <host>

# --port and -- host are optional, the default port is 2121 and the default host is localhost
```



