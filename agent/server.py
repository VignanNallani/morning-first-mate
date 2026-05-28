from flask import Flask, request, jsonify
from flask_cors import CORS
from agent import get_morning_briefing, chat

app = Flask(__name__)
CORS(app)

conversation_history = []

@app.route('/briefing', methods=['GET'])
def briefing():
    try:
        result = get_morning_briefing()
        return jsonify({"status": "success", "briefing": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    global conversation_history
    try:
        data = request.json
        user_message = data.get('message', '')
        response = chat(user_message, conversation_history)
        conversation_history.append({"role": "user", "content": user_message})
        conversation_history.append({"role": "assistant", "content": response})
        return jsonify({"status": "success", "response": response})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "agent": "Morning First Mate"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
