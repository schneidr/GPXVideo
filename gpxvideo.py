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
                    default=3)
parser.add_argument('--trackcolor', choices=['black', 'blue', 'brown', 'green', 'orange', 'purple',
                                             'red', 'white', 'yellow'],
                    help='Color of the track',
                    default='red')
parser.add_argument('--maptype', choices=['none', 'osm'],
                    help='Map style to use for the background',
                    default='osm')
args = parser.parse_args()

gpx_file = open(args.gpxfile.name, 'r')
gpx = gpxpy.parse(gpx_file)

tmpdir = tempfile.TemporaryDirectory(prefix='gpx', suffix=args.gpxfile.name)

context = staticmaps.Context()

if args.maptype == 'none':
    context.set_tile_provider(staticmaps.tile_provider_None)
elif args.maptype == 'osm':
    context.set_tile_provider(staticmaps.tile_provider_OSM)
else:
    sys.exit('invalid maptype')

if args.trackcolor == 'black':
    color = staticmaps.BLACK
elif args.trackcolor == 'blue':
    color = staticmaps.BLUE
elif args.trackcolor == 'brown':
    color = staticmaps.BROWN
elif args.trackcolor == 'green':
    color = staticmaps.GREEN
elif args.trackcolor == 'red':
    color = staticmaps.RED
elif args.trackcolor == 'orange':
    color = staticmaps.ORANGE
elif args.trackcolor == 'purple':
    color = staticmaps.PURPLE
elif args.trackcolor == 'white':
    color = staticmaps.WHITE
elif args.trackcolor == 'yellow':
    color = staticmaps.YELLOW
else:
    sys.exit('invalid trackcolor')

count: int = 0
points: list = []
image_files: list = []
for track in gpx.tracks:
    for segment in track.segments:
        bounds = staticmaps.Area(
                [staticmaps.create_latlng(point.latitude, point.longitude) for point in segment.points],
                fill_color=staticmaps.TRANSPARENT,
                width=(args.trackwidth+15),
                color=staticmaps.TRANSPARENT,
            )
        context.add_object(bounds)
        
for track in gpx.tracks:
    for segment in track.segments:
        print("Creating image files ...")
        progress = default_bar_logger('bar')
        for point in progress.iter_bar(points=segment.points):
            count += 1
            latlng = staticmaps.create_latlng(point.latitude, point.longitude)
            points.append(latlng)
            if count > 1:
                outline = staticmaps.Line(points, color=staticmaps.BLACK, width=(args.trackwidth+1))
                context.add_object(outline)
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
                context._objects.remove(outline)
clip = moviepy.video.io.ImageSequenceClip.ImageSequenceClip(image_files, fps=args.fps)
clip.write_videofile(re.sub(r'.gpx$', '.mp4', args.gpxfile.name), logger='bar')
shutil.rmtree(tmpdir.name)
