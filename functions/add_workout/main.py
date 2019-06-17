#import os
import gpxpy
#from google.cloud.datastore.helpers import GeoPoint # https://googleapis.github.io/google-cloud-python/latest/index.html
#from google.cloud.firestore_v1beta1 import GeoPoint
from firebase_admin.firestore import GeoPoint
import firebase_admin
from firebase_admin import firestore, auth
from workout import Workout, Track, Segment
from flask import abort, jsonify
from dataclasses import asdict


def init_firebase():
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

    if(request.method != 'POST'):
        raise Exception('Invalid request method.')

    # get auth token
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        raise Exception('Missing auth header')
    
    try:
        id_token = auth_header.split(" ")[1]
    except IndexError:
        raise Exception('Invalid auth header')
    
    try:
        decoded_token = auth.verify_id_token(id_token) # not checking if revoked
    except ValueError:
        raise Exception('Invalid token')

    uid = decoded_token['uid']

    # TODO: check file size

    name = request.form.get('name')
    if (not name):
        abort(make_error(400, 'nameRequired', 'Harjoituksen nimi vaaditaan.'))
   
    gpx_file = request.files.get('file')
    if (not gpx_file):
        abort(make_error(400, 'fileRequired', 'GPX-tiedosto vaaditaan.'))
    
    sport = request.form.get('sport')
    description = request.form.get('description')

    try:
        # read and decode file because gpxpy cannot read file in binary mode
        gpx_string = gpx_file.read().decode('utf-8')
        gpx = gpxpy.parse(gpx_string)
        workout = Workout(gpx, name, uid, sport=sport, description=description)
    except Exception as e:
        print(e)
        abort(make_error(400, 'fileInvalid', 'Virheellinen GPX-tiedosto.')) # TODO: add own expetion

    if (not save_workout(workout)):
        abort(make_error(400, 'saveFailed', 'Harjoituksen tallentaminen epäonnistui.'))
    
    #TODO: return 201 Created (and added object?) 

    return jsonify({'name': name, 'filename':gpx_file.filename})


def make_error(status_code, error_code, message):
    response = jsonify({
        'code': error_code,
        'message': message
    })
    response.status_code = status_code
    return response

def save_workout(workout):
    # convert workout to dict
    workout_dict = asdict(workout)
    # move track dicts to seprate list, they will be saved in a subcollection
    tracks = workout_dict.pop('tracks')
    if(not isinstance(tracks, list)):
        print('Workout does not contain tracks list. Should have atleast an empty list.')
        return False
    
    # get firestore client, api docs here https://googleapis.github.io/google-cloud-python/latest/firestore/client.html
    db = firestore.client()
    batch = db.batch()
    workout_ref = db.collection('workouts').document()
    batch.set(workout_ref, workout_dict)

    track_subcollection_ref = workout_ref.collection('tracks')
    for track in tracks:
        track_ref = track_subcollection_ref.document()
        batch.set(track_ref, track)
    
    batch.commit() #TODO: error handeling?
    return True



init_firebase()
