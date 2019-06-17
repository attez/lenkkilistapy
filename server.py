from functions.add_workout.main import add_workout
#TODO: fix import, must use absolute import in main.py but then this is not working

# When using the outside firebase project environment you need set up service account credentials
# https://firebase.google.com/docs/admin/setup/
# Also set up config(?) https://firebase.google.com/docs/reference/admin/python/firebase_admin#initialize_app
# Windows Powershell
# $env:GOOGLE_APPLICATION_CREDENTIALS="C:\Users\Atte\Documents\ERIKOIS\lenkkilista-firebase-adminsdk-yrla6-048b5c181c.json"

# for local debugging
if __name__ == "__main__":
    from flask import Flask, request
    from flask_cors import CORS
    import logging

    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('flask_cors').level = logging.DEBUG

    app = Flask(__name__)
    CORS(app) # default settings allow all cors requests

    @app.route('/addworkout', methods=['POST'])
    def index():
        return add_workout(request)

    app.run('127.0.0.1', 8000, debug=True)
