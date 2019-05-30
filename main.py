#import os
import gpxpy
from google.cloud.datastore.helpers import GeoPoint # https://googleapis.github.io/google-cloud-python/latest/index.html
import firebase_admin
from workout import Workout, Track, Segment
from flask import abort, jsonify
from dataclasses import asdict



#TODO
def init_firebase():
    # when using the outside firebase project environment you need set up service account credentials
    # https://firebase.google.com/docs/admin/setup/
    # Also set up config(?) https://firebase.google.com/docs/reference/admin/python/firebase_admin#initialize_app
    app = firebase_admin.initialize_app()



def add_workout(request):
    """ Parses a 'multipart/form-data' upload request
    Args:
        request (flask.Request): The request object.
    Returns:
        The response text, or any set of values that can be turned into a
         Response object using `make_response`
        <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>.
    """


    # TODO: get auth and check it
    # TODO: check file size

    name = request.form.get('name')
    if (not name):
        abort(make_error(400, 'nameRequired', 'Harjoituksen nimi vaaditaan.'))
   
    gpx_file = request.files.get('file')
    if (not gpx_file):
        abort(make_error(400, 'fileRequired', 'GPX-tiedosto vaaditaan.'))
    
    sport = request.form.get('sport')
    description = request.form.get('description')

    # read and decode file because gpxpy cannot read file in binary mode
    gpx_string = gpx_file.read().decode('utf-8')
    gpx = gpxpy.parse(gpx_string)
    workout = Workout(gpx, name)
    workout_dict = asdict(workout)
    # move tracks to seprate dictionary, they will be saved in a subcollection
    tracks_dict = workout_dict.pop('tracks')

    #TODO: save dicts to db (batch)

    #TODO: return 201 Created (and added object?) 

    return jsonify({'name': name, 'filename':gpx_file.filename})




def make_error(status_code, error_code, message):
    response = jsonify({
        'code': error_code,
        'message': message
    })
    response.status_code = status_code
    return response
    

# for local debugging
if __name__ == "__main__":
    from flask import Flask, request
    app = Flask(__name__)

    @app.route('/', methods=['GET', 'POST'])
    def index():
        return add_workout(request)

    app.run('127.0.0.1', 8000, debug=True)

