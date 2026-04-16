# 🚀 How to Run the 5G PCAN-5G Research Platform

## **RECOMMENDED: Simple One-Line Command**

Choose ONE of the following methods based on your preference:

### **Option 1: Python (Best for Cross-Platform)**
```bash
python start_all.py
```
- ✅ Works on Windows, macOS, Linux
- ✅ Handles all dependencies automatically
- ✅ Best error handling and output
- **Recommended for most users**

### **Option 2: Windows Batch Script**
```bash
start_all.bat
```
- ✅ Windows native script
- ✅ Opens services in separate command windows
- ✅ Easy to understand Windows command flow

### **Option 3: PowerShell Script**
```powershell
.\start_all.ps1
```
- ✅ Modern Windows approach
- ✅ Better process management
- ✅ Requires: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

---

## 📊 What Each Script Does

All scripts perform the following steps automatically:

1. ✓ **Install Python dependencies** (FastAPI, PyTorch, etc.)
2. ✓ **Install Node.js dependencies** (React, Vite, etc.)
3. ✓ **Start FastAPI Backend Server** on `http://localhost:8000`
4. ✓ **Start Vite Frontend Dev Server** on `http://localhost:5173`
5. ✓ **Open Frontend in default browser**

---

## 🎯 Access Your Application

Once running, you can access:

| Service | URL |
|---------|-----|
| **Frontend Dashboard** | http://localhost:5173 |
| **Backend API** | http://localhost:8000 |
| **API Documentation (Swagger)** | http://localhost:8000/docs |
| **Interactive API Tester (ReDoc)** | http://localhost:8000/redoc |

---

## 🔧 Manual Steps (If Automated Scripts Don't Work)

### Terminal 1 - Start Backend:
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Terminal 2 - Start Frontend:
```bash
cd frontend
npm install
npm run dev
```

---

## ⚙️ System Requirements

- **Python 3.8+** (with pip)
- **Node.js 16+** (with npm)
- **Ports available:** 8000 (backend), 5173 (frontend)

### Check if you have them:
```bash
python --version
npm --version
node --version
```

---

## 🐛 Troubleshooting

### Port 8000 already in use:
```bash
# Find process using port 8000
netstat -ano | findstr :8000
# Kill process (replace PID with the number found)
taskkill /PID <PID> /F
```

### Port 5173 already in use:
```bash
# Find process using port 5173
netstat -ano | findstr :5173
# Kill process (replace PID with the number found)
taskkill /PID <PID> /F
```

### Dependency installation errors:
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Then retry
python start_all.py
```

### npm not found:
- Download and install Node.js from https://nodejs.org/
- Restart your terminal/IDE after installation

---

## 📝 Project Structure

```
.
├── start_all.py          ← Main startup script (Python)
├── start_all.bat         ← Alternative for Windows (Batch)
├── start_all.ps1         ← Alternative for Windows (PowerShell)
├── backend/
│   ├── main.py           ← FastAPI server
│   ├── requirements.txt   ← Python dependencies
│   └── ...
└── frontend/
    ├── package.json      ← Node.js dependencies
    ├── vite.config.js    ← Vite configuration
    └── src/              ← React source files
```

---

## 💡 Quick Tips

- **Auto-reload on save:** Frontend uses Vite's hot-reload (automatic)
- **Backend hot-reload:** Modify `main.py` and the server will auto-reload
- **View logs:** Check the terminal windows for real-time logs
- **Stop everything:** Press `Ctrl+C` in the main terminal, or close the service windows

---

**That's it! You're ready to go! 🎉**
