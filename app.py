import os
import base64
from flask import Flask, render_template, request, jsonify, session
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file if present

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['SERVER_PORT'] = 5001  # Change port to avoid conflict
app.secret_key = os.urandom(24)  # For session management

# API key - get from environment
API_KEY = os.getenv('GEMINI_API_KEY', '')

# Default model - get from environment or use default
DEFAULT_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash')

# Default prompts
DEFAULT_SYSTEM_PROMPT = """
You are a personal finance assistant. 
Your tasks:
1) Analyze the user's spending history and provide insights into their habits.
2) Identify and label any recurring or automated transactions (e.g., daily commute costs, subscriptions).
3) Based on the analysis, propose a tailored weekly saving challenge for the user, detailing specific actions to reduce expenses and reach savings goals.
Format your response clearly, using tables or lists where helpful.
"""

@app.route('/')
def index():
    # Initialize session chat history if it doesn't exist
    if 'chat_history' not in session:
        session['chat_history'] = []
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    system_prompt = request.form.get('system_prompt', DEFAULT_SYSTEM_PROMPT)
    user_prompt = request.form.get('user_prompt', '')
    
    # Debug info
    app.logger.info(f"Received request: System prompt length: {len(system_prompt)}, User prompt: {user_prompt[:50]}...")
    
    # Check if API key is configured
    if not API_KEY:
        return jsonify({"error": "API key not configured. Please add your Gemini API key to the .env file."}), 400
    
    try:
        genai.configure(api_key=API_KEY)
        
        model = genai.GenerativeModel(DEFAULT_MODEL)
        app.logger.info(f"Using model: {DEFAULT_MODEL}")
        
        if 'chat_history' not in session:
            session['chat_history'] = []
            
        chat_history = session['chat_history'][-5:] if session['chat_history'] else []
        
        content = system_prompt
        
        # Process text file if uploaded
        file_content = ""
        if 'text_file' in request.files:
            text_file = request.files['text_file']
            if text_file and text_file.filename:
                try:
                    app.logger.info(f"Processing text file: {text_file.filename}")
                    file_content = text_file.read().decode('utf-8')
                    app.logger.info(f"File content length: {len(file_content)}")
                except Exception as e:
                    app.logger.error(f"Error processing text file: {str(e)}")
                    return jsonify({"error": f"Text file processing failed: {str(e)}"}), 500
        
        # Build prompt with file content and user prompt
        full_prompt = content
        
        # Add chat history context if available
        if chat_history:
            history_text = "Previous conversation:\n"
            for entry in chat_history:
                if entry['type'] == 'user':
                    history_text += f"User: {entry['text']}\n"
                else:
                    history_text += f"Assistant: {entry['text']}\n"
            full_prompt = f"{history_text}\n\nSystem: {full_prompt}"
        
        # Add file content if present
        if file_content:
            full_prompt += f"\n\nText file content:\n{file_content}"
        
        # Add user prompt if present
        if user_prompt:
            full_prompt += f"\n\nUser: {user_prompt}"
        
        app.logger.info("Sending request to model")
        response = model.generate_content(full_prompt)
        
        # Add this exchange to chat history
        if file_content:
            chat_history.append({'type': 'user', 'text': f"[Uploaded file: {request.files['text_file'].filename}] {user_prompt}"})
        else:
            chat_history.append({'type': 'user', 'text': user_prompt})
            
        chat_history.append({'type': 'assistant', 'text': response.text})
        
        # Update session
        session['chat_history'] = chat_history
        
        app.logger.info(f"Response length: {len(response.text)}")
        return jsonify({"response": response.text})
    
    except Exception as e:
        app.logger.error(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/clear_history', methods=['POST'])
def clear_history():
    session['chat_history'] = []
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True) 