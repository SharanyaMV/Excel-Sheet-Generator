import json
import re
from typing import Any, Dict, List


SUPPORTED_TYPES = {"string", "integer", "float", "date", "boolean"}
SUPPORTED_VISUALS = {
    "bar": ["bar chart", "bar graph", "bar"],
    "line": ["line chart", "line graph", "trend chart", "trend line", "line"],
    "pie": ["pie chart", "pie graph", "pie"],
    "scatter": ["scatter plot", "scatter chart", "scatter"],
}
EMPLOYEE_BASE_COLUMNS = [
    "Employee_ID",
    "Employee_Name",
    "First_Name",
    "Last_Name",
    "Gender",
    "Date_Of_Birth",
    "Age",
    "Email",
    "Phone_Number",
    "Address",
    "City",
    "State",
    "Country",
    "Postal_Code",
    "Department",
    "Job_Title",
    "Manager_Name",
    "Employment_Type",
    "Joining_Date",
    "Salary",
    "Bonus",
    "Work_Location",
    "Shift",
    "Employee_Status",
    "Experience_Years",
    "Education",
    "Skills",
    "Emergency_Contact_Name",
    "Emergency_Contact_Number",
    "Performance_Rating",
]


def detect_output_formats(user_prompt: str) -> List[str]:
    prompt = user_prompt.lower()
    wants_csv = bool(re.search(r"\b(csv|comma[- ]separated)\b", prompt))
    wants_excel = bool(re.search(r"\b(excel|xlsx|spreadsheet)\b", prompt))
    wants_both = "both" in prompt and (wants_csv or wants_excel)

    if wants_both or (wants_excel and wants_csv):
        return ["excel", "csv"]
    if wants_csv:
        return ["csv"]
    return ["excel"]


def detect_visuals(user_prompt: str) -> List[str]:
    prompt = user_prompt.lower()
    visuals = []
    for visual_type, aliases in SUPPORTED_VISUALS.items():
        if any(re.search(rf"\b{re.escape(alias)}s?\b", prompt) for alias in aliases):
            visuals.append(visual_type)
    return visuals


def _normalize_visuals(raw_visuals: Any, user_prompt: str = "") -> List[str]:
    if not raw_visuals:
        return detect_visuals(user_prompt)

    if isinstance(raw_visuals, str):
        return detect_visuals(raw_visuals)

    if not isinstance(raw_visuals, list):
        return detect_visuals(user_prompt)

    requested = []
    for item in raw_visuals:
        text = str(item).lower()
        for visual_type, aliases in SUPPORTED_VISUALS.items():
            if visual_type == text or any(alias in text for alias in aliases):
                requested.append(visual_type)
                break
    return list(dict.fromkeys(requested))


def _clean_name(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_ ]+", "", name).strip().replace(" ", "_")
    return cleaned or "Column"


def _infer_type(column_name: str, explicit_type: str = "") -> str:
    value = explicit_type.lower().strip()
    if value in {"int", "number", "numeric"}:
        return "integer"
    if value in {"decimal", "double", "currency", "money"}:
        return "float"
    if value in {"bool", "yes/no", "true/false"}:
        return "boolean"
    if value in SUPPORTED_TYPES:
        return value

    name = column_name.lower()
    if "date" in name or name.endswith("_at"):
        return "date"
    if "salary" in name or "price" in name or "amount" in name or "total" in name:
        return "float"
    if "id" in name or "age" in name or "count" in name or "quantity" in name:
        return "integer"
    if name.startswith("is_") or name.startswith("has_") or "active" in name:
        return "boolean"
    return "string"


def _normalize_columns(raw_columns: Any) -> List[Dict[str, str]]:
    columns = []
    if isinstance(raw_columns, str):
        raw_columns = [part.strip() for part in raw_columns.split(",") if part.strip()]

    if not isinstance(raw_columns, list):
        return columns

    for item in raw_columns:
        if isinstance(item, dict):
            name = _clean_name(str(item.get("name") or item.get("column") or "Column"))
            columns.append({"name": name, "type": _infer_type(name, str(item.get("type", "")))})
        else:
            text = str(item).strip()
            match = re.match(r"^(.+?)\s*[:(]\s*([A-Za-z/]+)\)?$", text)
            if match:
                name = _clean_name(match.group(1))
                columns.append({"name": name, "type": _infer_type(name, match.group(2))})
            elif text:
                name = _clean_name(text)
                columns.append({"name": name, "type": _infer_type(name)})

    return columns


def _requested_count(user_prompt: str, aliases: List[str], default: int) -> int:
    alias_pattern = "|".join(re.escape(alias) for alias in aliases)
    match = re.search(
        rf"\b(\d+)\s+(?:{alias_pattern})s?\b|\b(?:{alias_pattern})s?\s*[:=]?\s*(\d+)\b",
        user_prompt,
        re.IGNORECASE,
    )
    if not match:
        return default
    return int(next(value for value in match.groups() if value))


def _employee_columns(total_columns: int) -> List[Dict[str, str]]:
    names = EMPLOYEE_BASE_COLUMNS[:total_columns]
    if total_columns > len(names):
        names.extend(f"Employee_Field_{i:03d}" for i in range(len(names) + 1, total_columns + 1))
    return [{"name": name, "type": _infer_type(name)} for name in names]


def _schema_from_json(user_prompt: str) -> Dict[str, Any]:
    match = re.search(r"\{.*\}", user_prompt, flags=re.DOTALL)
    if not match:
        return {}

    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return {}

    sheet_name = _clean_name(str(data.get("sheet_name") or data.get("sheet") or "Data"))
    columns = _normalize_columns(data.get("columns", []))
    rows = int(data.get("rows", data.get("row_count", 10)))
    raw_formats = data.get("output_formats") or data.get("formats") or data.get("format")
    if isinstance(raw_formats, str):
        output_formats = detect_output_formats(raw_formats)
    elif isinstance(raw_formats, list):
        output_formats = [
            fmt for fmt in ("excel", "csv")
            if any(str(item).lower() in {fmt, "xlsx" if fmt == "excel" else "csv"} for item in raw_formats)
        ] or detect_output_formats(user_prompt)
    else:
        output_formats = detect_output_formats(user_prompt)
    return {
        "sheet_name": sheet_name,
        "columns": columns,
        "rows": max(rows, 1),
        "output_formats": output_formats,
        "visuals": _normalize_visuals(data.get("visuals") or data.get("charts"), user_prompt),
    }


def _schema_from_column_list(user_prompt: str) -> Dict[str, Any]:
    rows_match = re.search(r"\b(?:rows|row_count)\s*[:=]?\s*(\d+)\b", user_prompt, re.IGNORECASE)
    sheet_match = re.search(
        r"\b(?:sheet|sheet_name|file)\s*[:=]\s*(.+?)(?=\s+\bcolumns?\b|\s+\brows?\b|$)",
        user_prompt,
        re.IGNORECASE | re.DOTALL,
    )
    columns_match = re.search(
        r"\bcolumns?\s*[:=]\s*(.+?)(?:\brows?\s*[:=]?\s*\d+|$)",
        user_prompt,
        re.IGNORECASE | re.DOTALL,
    )

    if not columns_match:
        return {}

    columns_text = columns_match.group(1).strip(" .\n")
    columns = _normalize_columns(columns_text)
    if not columns:
        return {}

    sheet_name = _clean_name(sheet_match.group(1)) if sheet_match else "Data"
    rows = int(rows_match.group(1)) if rows_match else 10
    return {
        "sheet_name": sheet_name,
        "columns": columns,
        "rows": max(rows, 1),
        "output_formats": detect_output_formats(user_prompt),
        "visuals": detect_visuals(user_prompt),
    }


def generate_schema(user_prompt: str):
    explicit_schema = _schema_from_json(user_prompt) or _schema_from_column_list(user_prompt)
    if explicit_schema:
        return explicit_schema

    prompt_lower = user_prompt.lower()

    if "employee" in prompt_lower:
        sheet_name = "Employees"
        rows = _requested_count(user_prompt, ["row"], 10)
        total_columns = _requested_count(user_prompt, ["column", "col", "cloum", "cloumn"], len(EMPLOYEE_BASE_COLUMNS))
        columns = _employee_columns(total_columns)
    elif "customer" in prompt_lower:
        sheet_name, columns = "Customers", [
            {"name": "CustomerID", "type": "integer"},
            {"name": "Name", "type": "string"},
            {"name": "Email", "type": "string"}
        ]
        rows = 10
    elif "project" in prompt_lower or "task" in prompt_lower:
        sheet_name, columns = "Tasks", [
            {"name": "TaskID", "type": "integer"},
            {"name": "TaskName", "type": "string"},
            {"name": "Status", "type": "string"}
        ]
        rows = 10
    else:
        sheet_name, columns = "Data", [
            {"name": "ID", "type": "integer"},
            {"name": "Description", "type": "string"}
        ]
        rows = 10

    return {
        "sheet_name": sheet_name,
        "columns": columns,
        "rows": rows,
        "output_formats": detect_output_formats(user_prompt),
        "visuals": detect_visuals(user_prompt),
    }
