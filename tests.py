import gpxpy
from workout import Workout, Track, Segment

f = open('samples/2019-04-20.gpx', 'r', encoding='utf8')
gpx = gpxpy.parse(f)
w = Workout(gpx, 'testinimi')
