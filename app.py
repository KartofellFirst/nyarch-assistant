from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='.')
CORS(app)

# DeepSeek API configuration
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

if not DEEPSEEK_API_KEY:
    print("WARNING: DEEPSEEK_API_KEY not found in environment variables")

@app.route('/')
def index():
    """Serve the chat interface"""
    return send_from_directory('.', 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat requests to DeepSeek API"""
    try:
        data = request.json
        messages = data.get('messages', [])
        
        if not messages:
            return jsonify({'error': 'No messages provided'}), 400
        
        # Prepare the request to DeepSeek API
        headers = {
            'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': 'deepseek-chat',
            'messages': messages,
            'stream': False,
            'temperature': 0.7,
            'max_tokens': 2000
        }
        
        # Make request to DeepSeek API
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            assistant_message = result['choices'][0]['message']['content']
            return jsonify({'response': assistant_message})
        else:
            error_msg = f"DeepSeek API error: {response.status_code} - {response.text}"
            print(error_msg)
            return jsonify({'error': error_msg}), response.status_code
            
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Request timeout. Please try again.'}), 504
    except requests.exceptions.RequestException as e:
        print(f"Request error: {str(e)}")
        return jsonify({'error': f'Network error: {str(e)}'}), 500
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
