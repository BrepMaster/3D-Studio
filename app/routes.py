"""Flask routes module"""

from flask import render_template

from app.config import get_app, get_logger

app = get_app()
logger = get_logger()


@app.route('/')
def index():
    """Index page"""
    return render_template('index.html')


@app.route('/convert')
def convert():
    """Convert page"""
    return render_template('convert.html')


def run_server(host='0.0.0.0', port=5000, debug=True):
    """Run Flask server"""
    app.run(host=host, port=port, debug=debug, use_reloader=False, threaded=True)
