from flask import Flask, send_from_directory
import os
from app import app as flask_app

app = flask_app

@app.route('/')
def serve_html():
    return send_from_directory('../templates', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    if path.startswith('static/'):
        return send_from_directory('../', path)
    return send_from_directory('../templates', path) 