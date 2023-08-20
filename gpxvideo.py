import argparse
import gpxpy
import gpxpy.gpx
import moviepy.video.io.ImageSequenceClip
import os
from proglog import default_bar_logger
import s2sphere
import shutil
import staticmaps
import sys
import tempfile

parser = argparse.ArgumentParser(description='Create Video from GPX file')
# https://docs.python.org/3/library/argparse.html
parser.add_argument('--gpxfile', type=argparse.FileType('r'),
                    help='GPX file',
                    required=True)
parser.add_argument('--width', type=int,
                    help='Width of the output file',
                    default=1920)
parser.add_argument('--height', type=int,
                    help='Height of the output file',
                    default=1080)
parser.add_argument('--fps', type=int,
                    help='Frames per second',
                    default=30)
parser.add_argument('--trackwidth', type=int,
                    help='Width of the track',
                    default=10)
parser.add_argument('--trackcolor', choices=['red', 'green', 'blue'],
                    help='Color of the track',
                    default='blue')
parser.add_argument('--maptype', choices=['transparent', 'osm'],
                    help='Map style to use for the background',
                    default='osm')
args = parser.parse_args()

gpx_file = open(args.gpxfile.name, 'r')
gpx = gpxpy.parse(gpx_file)

tmpdir = tempfile.TemporaryDirectory(prefix='gpx', suffix=args.gpxfile.name)
print(tmpdir.name)

context = staticmaps.Context()

if args.maptype == 'transparent':
    sys.exit('--maptype transparent not implemented yet')
elif args.maptype == 'osm':
    context.set_tile_provider(staticmaps.tile_provider_OSM)
else:
    sys.exit('invalid maptype')

if args.trackcolor == 'red':
    color = (255, 0, 0)
elif args.trackcolor == 'green':
    color = (0, 255, 0)
elif args.trackcolor == 'blue':
    color = (0, 0, 255)
else:
    sys.exit('invalid trackcolor')

count: int = 0
for track in gpx.tracks:
    for segment in track.segments:
        lat_min: float = 99
        lng_min: float = 99
        lat_max: float = -99
        lng_max: float = -99
        for point in segment.points:
            if point.latitude < lat_min:
                lat_min = point.latitude
            if point.longitude < lng_min:
                lng_min = point.longitude
            if point.latitude > lat_max:
                lat_max = point.latitude
            if point.longitude > lng_max:
                lng_max = point.longitude

        bounds: s2sphere.LatLngRect = s2sphere.LatLngRect.from_point_pair(s2sphere.LatLng.from_degrees(lat_min, lng_min), s2sphere.LatLng.from_degrees(lat_max, lng_max))
        context.add_bounds(bounds)
        points = []
        progress = default_bar_logger('bar')
        for point in progress.iter_bar(points=segment.points):
            count += 1
            latlng = staticmaps.create_latlng(point.latitude, point.longitude)
            points.append(latlng)
            if count > 1:
                line = staticmaps.Line(points)
                context.add_object(line)
                filename = "{0}/{1:06d}.png".format(tmpdir.name, count)
                image = context.render_cairo(args.width, args.height)
                image.write_to_png(filename)
                context._objects.remove(line)
        image_files = [os.path.join(tmpdir.name,img)
               for img in os.listdir(tmpdir.name)
               if img.endswith(".png")]
        clip = moviepy.video.io.ImageSequenceClip.ImageSequenceClip(image_files, fps=args.fps)
        clip.write_videofile("{0}.mp4".format(args.gpxfile.name), logger='bar')
        shutil.rmtree(tmpdir.name)
