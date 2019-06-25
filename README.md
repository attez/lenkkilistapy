# lenkkilistapy
Google cloud function that can be used to calculate properties (distance, speed, elevation, ...) from GPX-files.
Properties are saved to Firebase firestore. Uses gpxpy-library.

## deployment
```
cd ./functions/add_workout
gcloud functions deploy  add_workout --runtime python37 --trigger-http
```

## local testing
```
python server.py
```
This a starts development server at localhost:8000.
