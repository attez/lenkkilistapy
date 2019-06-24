from functions.add_workout.main import add_workout

"""
    Used for testing Google cloud function locally.
    
    When using the outside firebase production environment you need set up service account credentials
    https://firebase.google.com/docs/admin/setup/
    Windows Powershell:
        $env:GOOGLE_APPLICATION_CREDENTIALS="path to firebase admin sdk json file" 

"""
if __name__ == "__main__":
    from flask import Flask, request
    from flask_cors import CORS
    import logging

    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('flask_cors').level = logging.DEBUG

    app = Flask(__name__)
    CORS(app) # default settings allows all cors requests

    @app.route('/addworkout/', methods=['POST'])
    def index():
        return add_workout(request)

    app.run('127.0.0.1', 8000, debug=True)
