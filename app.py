import os
import signal
from flask import Flask
from flask import jsonify
from application import misc

app = Flask(__name__)

signal.signal(signal.SIGINT, lambda s, f: os._exit(0))

@app.route("/")
def api_status():
    return jsonify({
        "status": "on" if misc.api_status() else "off"
        })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
