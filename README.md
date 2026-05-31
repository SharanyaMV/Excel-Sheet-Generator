# Google ADK Excel Generator Agent

## 📁 Project Structure (FIXED)

```
adk/
├── my_agent/
│   ├── __init__.py          # Package initialization
│   └── agent.py             # Root agent with Gemini integration
├── .adkignore               # Exclude patterns for ADK discovery
├── .env                     # Environment variables (GOOGLE_API_KEY)
├── .venv/                   # Python virtual environment
├── adk.yaml                 # ADK configuration (agent_discovery paths)
├── start_adk_web.py         # Convenience startup script
└── README.md                # This file
```

## ✅ Fixed Issues

1. ✅ **ValueError: No root_agent found for 'node_modules'** - RESOLVED
   - Added `.adkignore` file to exclude unwanted directories
   - Updated `adk.yaml` with explicit agent discovery paths
   - Structured agent code in proper `my_agent/` package

2. ✅ **Agent discovery** - Now limited to `./my_agent` only
3. ✅ **Root agent** - Properly defined in `my_agent/agent.py`
4. ✅ **Package structure** - Added `__init__.py` files
5. ✅ **Node modules excluded** - Fully ignored by ADK framework

## 🚀 Quick Start

### 1. Activate Virtual Environment
```powershell
cd c:\Users\HONNAVI VENU\OneDrive\Desktop\adk
.venv\Scripts\activate
```

### 2. Verify .env File
```
GOOGLE_API_KEY=your_api_key_here
```

### 3. Start ADK Web Server

**Recommended - Using startup script:**
```powershell
.venv\Scripts\python.exe start_adk_web.py
```

**Or direct command:**
```powershell
.venv\Scripts\python.exe -m google.adk web
```

### 4. Access Web Interface
Open: **http://localhost:8080**

## 🔧 Key Files

### my_agent/agent.py
- Defines `root_agent` (required by ADK)
- Integrates with Gemini 2.5 Flash
- Contains `excel_generator` tool
- Properly exported via `__all__`

### my_agent/__init__.py
- Package initialization
- Exports `root_agent` and `excel_generator`

### adk.yaml
```yaml
agent_discovery:
  paths:
    - ./my_agent          # Only scan this directory
  exclude_patterns:
    - node_modules
    - .venv
    - __pycache__
```

### .adkignore
- Prevents ADK from scanning irrelevant directories
- Includes: node_modules, .venv, __pycache__, .git, etc.

## 📊 Features

- 🤖 **AI-Powered**: Uses Google Gemini 2.5 Flash for intelligent Excel schema generation
- 📊 **Dynamic Excel Creation**: Generates Excel files with appropriate columns and sample data
- 🌐 **ADK Web UI**: Files are returned as downloadable artifacts in the ADK Web interface
- 🔧 **Flexible Schema**: Supports various spreadsheet types (employees, customers, products, projects, etc.)
- 📁 **Memory-Based**: No disk I/O - files generated in memory and returned as artifacts

## Installation

1. **Install Dependencies:**
   ```bash
   pip install google-adk pandas openpyxl python-dotenv google-generativeai
   ```

   Or using requirements.txt:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up Environment:**
   Create a `.env` file with your Google API key:
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   ```

## Usage

### Option 1: Run with ADK Web UI (Recommended)

1. **Start the ADK Web Interface:**
   ```bash
   adk web
   ```

2. **Access the Web UI:**
   Open your browser to `http://localhost:8080`

3. **Chat with the Agent:**
   Enter natural language requests like:
   - "Create a project management sheet with columns for ProjectID, ProjectName, StartDate, EndDate, and Status"
   - "Generate an employee database with Employee_ID, Name, Department, Salary, Email"
   - "Make a customer list with CustomerID, Name, Email, Phone, Address"

4. **Download Files:**
   Generated Excel files appear as downloadable artifacts in the ADK Web UI

### Option 2: Run as Command-Line Tool

```bash
cd /path/to/adk/project
python agent.py
```

Then enter your requirements interactively.

## Supported Spreadsheet Types

The agent automatically recognizes and creates appropriate schemas for:

- **Employee Databases**: Employee_ID, Name, Department, Salary, Email
- **Customer Lists**: CustomerID, Name, Email, Phone, Address
- **Product Inventories**: ProductID, ProductName, Category, Price, Stock
- **Project Management**: ProjectID, ProjectName, StartDate, EndDate, Status
- **Task Management**: TaskID, TaskName, Priority, DueDate, Status
- **Sales Tracking**: SaleID, CustomerName, Product, Quantity, Price, TotalAmount
- **Financial Reports**: Date, Description, Income, Expenses, Balance

## Example Requests

```
"Create a project management sheet with columns for ProjectID, ProjectName, StartDate, EndDate, and Status"
"Generate an employee database with ID, Name, Department, Salary"
"Make a customer list with CustomerID, Name, Email, Phone"
"Build a product inventory with ProductID, Name, Price, Stock"
"Create a sales report with SaleID, Customer, Product, Amount"
```

## Architecture

- **`agent.py`**: Main ADK agent configuration and runner
- **`tools.py`**: Excel generation logic using pandas and openpyxl
- **`schema.py`**: Schema generation from natural language
- **`adk.yaml`**: ADK configuration for web deployment
- **`.env`**: Environment variables (API keys)

## File Generation Process

1. **User Request** → Natural language description
2. **Schema Generation** → Parse request and determine columns/types
3. **Excel Creation** → Generate file in memory using pandas
4. **ADK Artifact** → Return as downloadable file in Web UI

## Error Handling

- Invalid requests are handled gracefully with helpful error messages
- API failures are caught and reported
- File generation errors are logged and communicated to user

## Requirements

- Python 3.8+
- Google Cloud API key with Gemini API access
- Internet connection for API calls

## License

This project demonstrates Google ADK integration for Excel generation.