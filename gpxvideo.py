import argparse
import gpxpy
import gpxpy.gpx
import moviepy.video.io.ImageSequenceClip
from proglog import default_bar_logger
import re
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
                    default=2)
parser.add_argument('--trackcolor', choices=['red', 'green', 'blue'],
                    help='Color of the track',
                    default='red')
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
        bounds = staticmaps.Area(
                [staticmaps.create_latlng(point.latitude, point.longitude) for point in segment.points],
                fill_color=staticmaps.TRANSPARENT,
                width=2,
                color=staticmaps.TRANSPARENT,
            )
        context.add_object(bounds)
        
        points: list = []
        image_files: list = []
        print("Creating image files ...")
        progress = default_bar_logger('bar')
        for point in progress.iter_bar(points=segment.points):
            count += 1
            latlng = staticmaps.create_latlng(point.latitude, point.longitude)
            points.append(latlng)
            if count > 1:
                line = staticmaps.Line(points, color=color, width=args.trackwidth)
                context.add_object(line)
                marker = staticmaps.ImageMarker(latlng, "marker_dot.png", origin_x=5, origin_y=5)
                context.add_object(marker)
                filename = "{0}/{1:06d}.png".format(tmpdir.name, count)
                image = context.render_cairo(args.width, args.height)
                image.write_to_png(filename)
                image_files.append(filename)
                context._objects.remove(line)
                context._objects.remove(marker)
        clip = moviepy.video.io.ImageSequenceClip.ImageSequenceClip(image_files, fps=args.fps)
        clip.write_videofile(re.sub(r'.gpx$', '.mp4', args.gpxfile.name), logger='bar')
        shutil.rmtree(tmpdir.name)
