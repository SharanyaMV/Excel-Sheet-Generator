# 🚀 ADK WEB SERVER - QUICK START GUIDE

## Complete Step-by-Step Instructions

### **Step 1: Open PowerShell**
```
Press: Win + R
Type: powershell
Press: Enter
```

### **Step 2: Navigate to Project Directory**
```powershell
cd "c:\Users\HONNAVI VENU\OneDrive\Desktop\adk"
```

### **Step 3: Activate Virtual Environment**
```powershell
.venv\Scripts\Activate.ps1
```

You should see `(.venv)` in your terminal prompt.

If you get an error about execution policy, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### **Step 4: Verify Setup (Optional but Recommended)**
```powershell
# Check if root_agent exists
python -c "from my_agent.agent import root_agent; print('✅ root_agent loaded successfully')"

# Check ADK is installed
python -c "import google.adk; print(f'✅ ADK version {google.adk.__version__}')"
```

### **Step 5: Start ADK Web Server**

**RECOMMENDED METHOD:**
```powershell
python -m google.adk web
```

**ALTERNATIVE METHOD:**
```powershell
python start_adk_web.py
```

### **Step 6: Wait for Server to Start**

You should see output like:
```
🚀 Starting Excel Generator Agent Web Interface...
🌐 Web interface will be available at http://localhost:8080
 * Running on http://127.0.0.1:8080
 * Running on http://10.181.47.125:8080
```

### **Step 7: Open Web Browser**

Navigate to: **http://localhost:8080**

### **Step 8: Create Excel Files**

1. Type your requirement in the text box
2. Click "Generate Excel"
3. Download your file

---

## ✅ Common Startup Messages (All Normal)

```
✅ "Agent discovery initialized"
✅ "Loading agent from ./my_agent"
✅ "root_agent registered successfully"
✅ "Running on http://127.0.0.1:8080"
✅ "Debugger PIN:"
```

---

## ❌ Common Startup Errors (FIXED)

### Error 1: "ValueError: No root_agent found"
**Status**: ✅ FIXED
**Why**: Now using agent_discovery with exclude_patterns

### Error 2: "node_modules ValueError"
**Status**: ✅ FIXED
**Why**: .adkignore and adc.yaml exclude node_modules

### Error 3: "ModuleNotFoundError: No module named 'my_agent'"
**Status**: ✅ FIXED
**Why**: __init__.py files created

---

## 🆘 Troubleshooting

### Problem: "Port 8080 already in use"
```powershell
# Kill Python processes
Get-Process python | Stop-Process -Force

# Or use different port by editing adc.yaml:
# Change: port: 8080
# To:     port: 8081
```

### Problem: ".env file not found"
```powershell
# Verify .env exists and contains:
Get-Content .env

# If missing:
echo GOOGLE_API_KEY=your_key_here > .env
```

### Problem: "RESOURCE_EXHAUSTED" error (API quota)
**Status**: Expected behavior (free tier: 20 requests/day)
**Solution**: Wait 24 hours or upgrade your API plan

### Problem: Stuck on "Processing..."
1. Wait 30 seconds for response
2. Check browser console for errors (F12)
3. Check terminal for error messages
4. Restart server if necessary

---

## 📊 Terminal Session Example

```powershell
PS C:\Users\HONNAVI VENU\OneDrive\Desktop> cd adk

PS C:\Users\HONNAVI VENU\OneDrive\Desktop\adk> .venv\Scripts\Activate.ps1
(.venv) PS C:\Users\HONNAVI VENU\OneDrive\Desktop\adk>

(.venv) PS C:\Users\HONNAVI VENU\OneDrive\Desktop\adk> python -m google.adk web
🚀 Starting Excel Generator Agent Web Interface...
🌐 Web interface will be available at http://localhost:8080
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:8080
 * Press CTRL+C to quit
```

Then open browser to: **http://localhost:8080**

---

## 📋 Checklist Before Startup

- [ ] Virtual environment activated (.venv in prompt)
- [ ] .env file exists with GOOGLE_API_KEY
- [ ] my_agent/agent.py exists
- [ ] my_agent/__init__.py exists
- [ ] adc.yaml has agent_discovery config
- [ ] .adkignore exists
- [ ] Port 8080 is available
- [ ] Internet connection active

---

## 🎯 What Happens Next

1. **Server starts**: Loads my_agent/agent.py
2. **Discovers root_agent**: From my_agent.agent module
3. **Initializes web UI**: Available at http://localhost:8080
4. **Listens for requests**: Ready for Excel generation

---

## 📞 Support

If you encounter issues:

1. Run verification: `python verify_structure.py`
2. Check file contents: `type my_agent\agent.py`
3. Test imports: `python -c "from my_agent.agent import root_agent"`
4. Review logs in terminal output
5. Consult SETUP_GUIDE.md for detailed troubleshooting

---

**Last Updated**: May 8, 2026
**Status**: ✅ Project Ready
**Next Step**: Run `python -m google.adk web`
