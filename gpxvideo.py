import argparse
import gpxpy
import gpxpy.gpx
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

def write_image(line: list, filename: str, args):
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

    context.add_object(staticmaps.Line(points))

    image = context.render_cairo(args.width, args.height)
    image.write_to_png(filename)

count: int = 0
for track in gpx.tracks:
    for segment in track.segments:
        points = []
        for point in segment.points:
            count += 1
            latlng = staticmaps.create_latlng(point.latitude, point.longitude)
            points.append(latlng)
            if count > 1:
                filename = "{0}/{1:06d}.png".format(tmpdir.name, count)
                print(filename)
                write_image(points, filename, args)

