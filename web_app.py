import os
import tempfile
from flask import Flask, request, jsonify, send_file
import asyncio
import io
import base64
from agent import excel_generator, create_runner, session_service
from google.adk.runners import Runner
from google.genai import types

app = Flask(__name__)

# Global variables for session management
runner = None
session_id = None
temp_dir = tempfile.mkdtemp()

@app.before_request
def setup_agent():
    global runner, session_id
    if runner is None:
        runner = create_runner()
        # Note: We can't await here, so we'll create session in the generate function
        session_id = None

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Excel Generator Agent</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .container { background: #f5f5f5; padding: 20px; border-radius: 8px; }
            textarea { width: 100%; height: 100px; margin: 10px 0; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background: #0056b3; }
            .result { margin-top: 20px; padding: 10px; background: white; border-radius: 4px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Excel Generator Agent</h1>
            <p>Describe the Excel file you want to create:</p>
            <form id="excelForm">
                <textarea id="requirement" placeholder="e.g., Create a project management sheet with columns for ProjectID, ProjectName, StartDate, EndDate, and Status"></textarea>
                <br>
                <button type="submit">Generate Excel</button>
            </form>
            <div id="result" class="result" style="display: none;"></div>
        </div>

        <script>
            document.getElementById('excelForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                const requirement = document.getElementById('requirement').value;
                const resultDiv = document.getElementById('result');

                resultDiv.style.display = 'block';
                resultDiv.innerHTML = '🤔 Processing your request...';

                try {
                    const response = await fetch('/generate', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ requirement: requirement })
                    });

                    const data = await response.json();

                    if (data.success) {
                        resultDiv.innerHTML = `
                            <h3>✅ Success!</h3>
                            <p>${data.message}</p>
                            <p><strong>File:</strong> ${data.file_name}</p>
                            <p><strong>Columns:</strong> ${data.columns.join(', ')}</p>
                            <p><strong>Rows:</strong> ${data.row_count}</p>
                            <a href="/download/${data.file_name}" target="_blank">
                                <button>⬇️ Download ${data.file_name}</button>
                            </a>
                        `;
                    } else {
                        resultDiv.innerHTML = `<h3>❌ Error</h3><p>${data.message}</p>`;
                    }
                } catch (error) {
                    resultDiv.innerHTML = `<h3>❌ Error</h3><p>${error.message}</p>`;
                }
            });
        </script>
    </body>
    </html>
    '''

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json()
        requirement = data.get('requirement', '')

        if not requirement:
            return jsonify({'success': False, 'message': 'Please provide a requirement'})

        # Run agent synchronously using asyncio.run
        result = asyncio.run(run_agent(requirement))

        if result.get('status') == 'error':
            return jsonify({'success': False, 'message': result['message']})

        return jsonify({
            'success': True,
            'message': result.get('message', 'Excel generated successfully'),
            'file_name': result.get('file_name', 'Unknown.xlsx'),
            'columns': result.get('columns', []),
            'row_count': result.get('row_count', 0)
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

async def run_agent(requirement):
    """Run the agent with the given requirement"""
    try:
        # Create message for ADK
        content = types.Content(
            role="user",
            parts=[types.Part(text=requirement)]
        )

        # Get or create runner
        global runner, session_id
        if runner is None:
            runner = create_runner()
        if session_id is None:
            session = await session_service.create_session(app_name="excel_generator_app", user_id="web_user")
            session_id = session.id

        # Run agent
        events = runner.run(
            user_id="web_user",
            session_id=session_id,
            new_message=content
        )

        # Process events
        for event in events:
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        # Check if this is a function call result
                        if 'function_call' in part.text:
                            continue

            # Handle file artifacts
            if hasattr(event, 'artifacts') and event.artifacts:
                for artifact in event.artifacts:
                    if artifact.get('artifact_type') == 'file':
                        # Save file to temp directory
                        file_name = artifact.get('file_name', 'Generated.xlsx')
                        file_data_b64 = artifact.get('file_data', '')
                        if file_data_b64:
                            file_data = base64.b64decode(file_data_b64)
                            file_path = os.path.join(temp_dir, file_name)
                            with open(file_path, 'wb') as f:
                                f.write(file_data)

                            return {
                                'message': f'Excel file \'{file_name}\' generated successfully with {len(artifact.get("columns", []))} columns and {artifact.get("row_count", 0)} rows.',
                                'file_name': file_name,
                                'file_path': file_path,
                                'columns': artifact.get('columns', []),
                                'row_count': artifact.get('row_count', 0)
                            }

        # If no artifacts found, try the direct tool approach
        result = excel_generator(requirement)
        if result.get('status') != 'error' and result.get('file_data'):
            # Save file from direct tool call
            file_name = result.get('file_name', 'Generated.xlsx')
            file_data_b64 = result.get('file_data', '')
            if file_data_b64:
                file_data = base64.b64decode(file_data_b64)
                file_path = os.path.join(temp_dir, file_name)
                with open(file_path, 'wb') as f:
                    f.write(file_data)

                return {
                    'message': f'Excel file \'{file_name}\' generated successfully with {len(result.get("columns", []))} columns and {result.get("row_count", 0)} rows.',
                    'file_name': file_name,
                    'file_path': file_path,
                    'columns': result.get('columns', []),
                    'row_count': result.get('row_count', 0)
                }

        return result

    except Exception as e:
        return {'status': 'error', 'message': str(e)}

@app.route('/download/<filename>')
def download(filename):
    file_path = os.path.join(temp_dir, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True, download_name=filename)
    else:
        return f"File {filename} not found", 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)