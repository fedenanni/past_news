"""Minimal test endpoint to verify Vercel Python runtime."""
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET'])
def test():
    """Simple test endpoint."""
    return jsonify({
        'status': 'ok',
        'message': 'Vercel Python function is working!'
    })

if __name__ == '__main__':
    app.run(debug=True)
