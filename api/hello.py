"""Minimal WSGI test endpoint."""

def handler(event, context):
    """Simple handler for Vercel."""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': '{"status": "ok", "message": "Python is working!"}'
    }
