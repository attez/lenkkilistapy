import gpxpy
from firebase_admin.firestore import GeoPoint
import firebase_admin
from firebase_admin import firestore, auth
from flask import abort, jsonify
from dataclasses import asdict

from workout import Workout, Track, Segment


""" 
    Entry point for the cloud function.
    Parses a 'multipart/form-data' upload request that contains information for a workout
    including a gpx file. Workout is saved to Firestore database.
    Args:
        request (flask.Request): The request object.
    Returns:
        200 OK response if workout is added, otherwise 400 with JSON error response.
"""
def add_workout(request):
    try:
        return add_workout_to_firestore(request)
    except InvalidUsage as e:
        return e.to_response()  # return response without exception, no error logging
    except Exception as e:
        raise e # this will show up in google error reporting console

""" 
    Args:
        request (flask.Request): The request object.
        
        Must be a POST request with a form data. 

        Must contain Authorization header and valid Firebase user token.
        
        Formfields:
        - name (required)
        - file (required)
        - sport
        - description

    Returns:
        200 OK response if workout is added, otherwise raises InvalidUsage Exception
"""
def add_workout_to_firestore(request):
    # headers and form data
    check_request_method(request, ['POST'])
    uid = get_uid(request)
    check_file_size(request)
    name = get_name(request)
    gpx_file = get_file(request)
    sport = get_sport(request)
    description = get_description(request)

    # parse gpx to workout
    try:
        # read and decode file because gpxpy cannot read file in binary mode
        gpx_string = gpx_file.read().decode('utf-8')
        gpx = gpxpy.parse(gpx_string)
        workout = Workout(gpx, name, uid, sport=sport, description=description)
    except Exception as e:
        print(e)
        raise InvalidUsage('Virheellinen GPX-tiedosto.', error_code='fileInvalid' )

    # save to firestore
    try:
        save_workout_to_firestore(workout)
    except Exception as e:
        print(e)
        raise InvalidUsage('Harjoituksen tallentaminen epäonnistui.', error_code='saveFailed')
    
    #TODO: return 201 Created (and workout object?) 

    return jsonify({'name': name, 'filename': gpx_file.filename})

def init_firebase():
    app = firebase_admin.initialize_app()

def check_request_method(request, allowed_methods):
    if(request.method not in allowed_methods):
        raise InvalidUsage('Invalid request method.')
    return request.method

def check_file_size(request):
    pass #TODO

# Authtenticates request using token in the request header.
def get_uid(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        raise InvalidUsage('Missing auth header')
    try:
        id_token = auth_header.split(" ")[1]
    except IndexError:
        raise InvalidUsage('Invalid auth header')
    
    try:
        decoded_token = auth.verify_id_token(id_token) # not checking if revoked
    except ValueError:
        raise InvalidUsage('Invalid token')

    return decoded_token['uid']

def get_name(request):
    name = request.form.get('name')
    if (not name):
        raise InvalidUsage('Harjoituksen nimi vaaditaan.', error_code='nameRequired')
    return name

def get_file(request):
    gpx_file = request.files.get('file')
    if (not gpx_file):
        raise InvalidUsage('GPX-tiedosto vaaditaan.', error_code='fileRequired')
    return gpx_file

def get_sport(request):
    return request.form.get('sport')

def get_description(request):
    return request.form.get('description')


def save_workout_to_firestore(workout):
    # convert workout to dict
    workout_dict = asdict(workout)
    # move track dicts to seprate list, they will be saved in a subcollection
    tracks = workout_dict.pop('tracks')
    if(not isinstance(tracks, list)):
        raise Exception('Workout does not contain tracks list. Should have atleast an empty list.')
    
    # get firestore client, api docs here https://googleapis.github.io/google-cloud-python/latest/firestore/client.html
    db = firestore.client()
    batch = db.batch()
    workout_ref = db.collection('workouts').document()
    batch.set(workout_ref, workout_dict)

    track_subcollection_ref = workout_ref.collection('tracks')
    for track in tracks:
        track_ref = track_subcollection_ref.document()
        batch.set(track_ref, track)
    
    batch.commit()
    return True


"""
Custom exception class that can contain detailed error information.
Error object can be turned into Response with to_response.
"""
class InvalidUsage(Exception):

    def __init__(self, message, error_code=None, status_code=400, payload=None):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.payload = payload

    def to_dict(self):
        error = dict(self.payload or ())
        error['message'] = self.message
        error['code'] = self.error_code
        return error

    def to_response(self):
        response = jsonify(self.to_dict()) # creates a Response with the JSON representation
        response.status_code = self.status_code
        return response
    

init_firebase()

# Google cloud function does not give access to flask app instance, this does not work with google cloud functions:
# @app.errorhandler(InvalidUsage)
# def handle_invalid_usage(error):
#     ...