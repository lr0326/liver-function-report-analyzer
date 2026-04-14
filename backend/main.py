"""
Application startup script.

Run with:
    python main.py
or via gunicorn:
    gunicorn -w 4 -b 0.0.0.0:5000 'main:app'
"""

from app.main import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
