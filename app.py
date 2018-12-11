from application import create_app

# Call the Application Factory function to construct a Flask application instance
# using the standard configuration defined in /instance/flask.cfg
app = create_app('development_config.cfg')

if __name__ == "__main__":
    app.socketio.run(host='0.0.0.0')
