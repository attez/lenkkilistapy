from main import add_workout

# for local debugging
if __name__ == "__main__":
    from flask import Flask, request
    from flask_cors import CORS
    import logging

    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('flask_cors').level = logging.DEBUG

    app = Flask(__name__)
    CORS(app) # default settings allow all cors requests

    @app.route('/', methods=['POST'])
    def index():
        return add_workout(request)

    app.run('127.0.0.1', 8000, debug=True)
