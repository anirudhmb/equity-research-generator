# Cross-Platform Setup Guide 🪟🍎

This guide ensures the project works seamlessly on both **Windows** and **macOS**.

---

## 🎯 Platform Support

✅ **macOS** (Intel & Apple Silicon)  
✅ **Windows 10/11**  
✅ **Linux** (Ubuntu/Debian)

---

## 📋 Prerequisites by Platform

### macOS
```bash
# Check Python version
python3 --version  # Should be 3.10+

# Homebrew (recommended for package management)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Windows
```powershell
# Check Python version
python --version  # Should be 3.10+

# Install Python from python.org if needed
# https://www.python.org/downloads/

# Chocolatey (optional, for package management)
# Run PowerShell as Administrator:
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

---

## 🐍 Virtual Environment Setup

### macOS/Linux
```bash
# Navigate to project
cd /path/to/equity-research-generator

# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate

# Verify
which python
# Should show: /path/to/project/venv/bin/python
```

### Windows (Command Prompt)
```cmd
# Navigate to project
cd C:\path\to\equity-research-generator

# Create virtual environment
python -m venv venv

# Activate
venv\Scripts\activate.bat

# Verify
where python
# Should show: C:\path\to\project\venv\Scripts\python.exe
```

### Windows (PowerShell)
```powershell
# Navigate to project
cd C:\path\to\equity-research-generator

# Create virtual environment
python -m venv venv

# You may need to enable script execution first:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Activate
.\venv\Scripts\Activate.ps1

# Verify
Get-Command python
# Should show path in venv folder
```

---

## 🤖 Ollama Installation

### macOS
```bash
# Download and install
curl -fsSL https://ollama.com/install.sh | sh

# Or using Homebrew
brew install ollama

# Start Ollama
ollama serve

# In another terminal, pull model
ollama pull llama3
```

### Windows
1. **Download**: Go to https://ollama.com/download/windows
2. **Install**: Run the downloaded `.exe` file
3. **Verify**: Open Command Prompt or PowerShell
   ```powershell
   ollama --version
   ```
4. **Pull Model**:
   ```powershell
   ollama pull llama3
   ```

**Note**: Ollama runs as a Windows service automatically after installation.

### Linux (Ubuntu/Debian)
```bash
# Install
curl -fsSL https://ollama.com/install.sh | sh

# Start service
sudo systemctl start ollama

# Pull model
ollama pull llama3
```

---

## 📦 Dependencies Installation

### Both Platforms

Create `requirements.txt`:
```bash
# Core Framework
langchain>=0.1.0
langgraph>=0.0.20
langchain-ollama>=0.0.1

# Alternative LLM options
langchain-groq  # For Groq API
langchain-google-genai  # For Gemini

# Data Collection
yfinance>=0.2.35
beautifulsoup4>=4.12.0
requests>=2.31.0
feedparser>=6.0.10

# Data Processing
pandas>=2.0.0
numpy>=1.24.0
scipy>=1.10.0

# Visualization
matplotlib>=3.7.0
seaborn>=0.12.0

# Document Generation
python-docx>=1.1.0
openpyxl>=3.1.0

# UI
streamlit>=1.28.0

# Utilities
python-dotenv>=1.0.0
```

Install:
```bash
# macOS/Linux
pip install -r requirements.txt

# Windows
pip install -r requirements.txt
```

---

## 🔧 Configuration for Cross-Platform

### File Paths (Important!)

**Always use pathlib for cross-platform paths:**

```python
# ✅ CORRECT - Works on all platforms
from pathlib import Path

base_dir = Path(__file__).parent
data_dir = base_dir / "data"
output_file = data_dir / "output.csv"

# ❌ WRONG - Only works on Unix
data_dir = "/Users/username/project/data"  # Mac/Linux only
output_file = "data/output.csv"  # Forward slash

# ❌ WRONG - Only works on Windows
data_dir = "C:\\Users\\username\\project\\data"  # Windows only
output_file = "data\\output.csv"  # Backslash
```

### Environment Variables

**Cross-platform `.env` file:**
```bash
# Works on both platforms
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434

# Don't use platform-specific paths in .env
# Use relative paths or configure at runtime
```

### Shell Scripts

Create both versions:

**`setup.sh`** (macOS/Linux):
```bash
#!/bin/bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
ollama pull llama3
echo "Setup complete! Run: source venv/bin/activate"
```

**`setup.bat`** (Windows Command Prompt):
```batch
@echo off
python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt
ollama pull llama3
echo Setup complete! Run: venv\Scripts\activate.bat
```

**`setup.ps1`** (Windows PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
ollama pull llama3
Write-Host "Setup complete! Run: .\venv\Scripts\Activate.ps1"
```

---

## 🏃 Running the Application

### macOS/Linux
```bash
# Activate venv
source venv/bin/activate

# Start Ollama (if not running)
ollama serve &

# Run application
streamlit run ui/app.py
```

### Windows (Command Prompt)
```cmd
# Activate venv
venv\Scripts\activate.bat

# Ollama should be running as service
# If not, start it manually

# Run application
streamlit run ui/app.py
```

### Windows (PowerShell)
```powershell
# Activate venv
.\venv\Scripts\Activate.ps1

# Run application
streamlit run ui/app.py
```

---

## 🐛 Platform-Specific Issues & Solutions

### macOS

**Issue**: Permission denied when running scripts
```bash
# Solution: Make script executable
chmod +x setup.sh
./setup.sh
```

**Issue**: Ollama not found
```bash
# Solution: Add to PATH or use full path
export PATH="/usr/local/bin:$PATH"
```

### Windows

**Issue**: PowerShell execution policy
```powershell
# Solution: Enable script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Issue**: Python not found
```cmd
# Solution: Add Python to PATH
# Control Panel → System → Advanced → Environment Variables
# Add: C:\Python310\Scripts and C:\Python310
```

**Issue**: Ollama connection error
```powershell
# Solution: Check Ollama service
# Services.msc → Find Ollama → Start

# Or restart Ollama
ollama serve
```

**Issue**: Long paths error
```powershell
# Solution: Enable long paths in Windows
# Run as Administrator:
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```

---

## 📝 Git Configuration (Cross-Platform)

### Line Endings

**.gitattributes** (create in project root):
```
# Auto detect text files and normalize to LF
* text=auto

# Force LF for shell scripts
*.sh text eol=lf

# Force CRLF for Windows batch files
*.bat text eol=crlf
*.ps1 text eol=crlf

# Binary files
*.png binary
*.jpg binary
*.xlsx binary
*.docx binary
```

### Git on Windows

```powershell
# Set line ending handling
git config --global core.autocrlf true

# Set SSH key (if using SSH)
git config --global core.sshCommand "ssh -i C:/Users/YourName/.ssh/id_ed25519_personal"
```

---

## 🧪 Testing Cross-Platform Compatibility

### Test Script

**`test_platform.py`**:
```python
import sys
import platform
from pathlib import Path

def test_platform():
    print(f"Platform: {platform.system()}")
    print(f"Python: {sys.version}")
    print(f"Architecture: {platform.machine()}")
    
    # Test path handling
    test_path = Path(__file__).parent / "data" / "test.csv"
    print(f"Test path: {test_path}")
    print(f"Path exists: {test_path.parent.exists()}")
    
    # Test imports
    try:
        import yfinance
        print("✅ yfinance installed")
    except ImportError:
        print("❌ yfinance not installed")
    
    try:
        import langchain
        print("✅ langchain installed")
    except ImportError:
        print("❌ langchain not installed")
    
    print("\nPlatform test complete!")

if __name__ == "__main__":
    test_platform()
```

Run on both platforms:
```bash
# macOS/Linux
python test_platform.py

# Windows
python test_platform.py
```

---

## 🚀 Deployment Considerations

### Docker (Cross-Platform Alternative)

If you want truly universal deployment:

**`Dockerfile`**:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "ui/app.py"]
```

**`docker-compose.yml`**:
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
      - ./outputs:/app/outputs
    environment:
      - LLM_PROVIDER=ollama
      - OLLAMA_BASE_URL=http://ollama:11434
  
  ollama:
    image: ollama/ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama

volumes:
  ollama_data:
```

Run on any platform:
```bash
docker-compose up
```

---

## ✅ Cross-Platform Checklist

Before deploying, verify:

- [ ] Used `pathlib.Path` for all file paths
- [ ] Used `os.path.join()` if pathlib not available
- [ ] No hardcoded forward/backslashes in paths
- [ ] No platform-specific commands in code
- [ ] Environment variables instead of hardcoded paths
- [ ] Tested on both Windows and macOS
- [ ] `.gitattributes` configured for line endings
- [ ] Setup scripts for both platforms
- [ ] Documentation includes both platforms
- [ ] Dependencies work on both platforms

---

## 📚 Additional Resources

**Python Cross-Platform:**
- pathlib: https://docs.python.org/3/library/pathlib.html
- os.path: https://docs.python.org/3/library/os.path.html

**Ollama:**
- macOS: https://ollama.com/download/mac
- Windows: https://ollama.com/download/windows

**Git:**
- Line endings: https://git-scm.com/book/en/v2/Customizing-Git-Git-Configuration

---

## 🆘 Getting Help

**Platform-specific issues:**
- macOS: Check Homebrew issues or system logs
- Windows: Check Event Viewer or Windows Security

**Community:**
- GitHub Issues: Report platform-specific bugs
- Discord/Slack: Ask community for help

---

**Both Windows and macOS are fully supported! 🎉**

