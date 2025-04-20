# Budgee - Financial Text Analysis

A sleek web interface for analyzing financial text files using Google's Gemini AI.

## Features

- Clean, minimalist black and white UI
- Upload text files for financial analysis
- Chatbot-style interaction with the AI
- Well-formatted responses

## Setup

1. Add your Gemini API key to the `.env` file:
   ```
   GEMINI_API_KEY="your_api_key_here"
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Run the Flask application:
   ```
   python app.py
   ```

4. Open your browser and navigate to `http://127.0.0.1:5000`

## Usage

1. Upload a text file (.txt) containing financial data
2. Customize the system prompt if needed (default is provided)
3. Optionally add a description or question about the text
4. Click "Analyze" to process the data
5. View the formatted results in the chat panel

## Requirements

- Python 3.7+
- Flask
- Google Generative AI library
- Internet connection for API access

## Note

You need a valid Google Gemini API key to use this application. You can obtain one from the [Google AI Studio](https://makersuite.google.com/app/apikey). 