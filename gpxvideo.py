import argparse
from gps_class import GPSVis
import gpxpy
import gpxpy.gpx
from PIL import Image, ImageDraw
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

def scale_to_img(lat_lon, startpos, h_w, points):
    """
    Conversion from latitude and longitude to the image pixels.
    It is used for drawing the GPS records on the map image.
    :param lat_lon: GPS record to draw (lat1, lon1).
    :param h_w: Size of the map image (w, h).
    :return: Tuple containing x and y coordinates to draw on map image.
    """
    # https://gamedev.stackexchange.com/questions/33441/how-to-convert-a-number-from-one-min-max-set-to-another-min-max-set/33445
    old = (points[2], points[0])
    new = (0, h_w[1])
    y = ((lat_lon[0] - old[0]) * (new[1] - new[0]) / (old[1] - old[0])) + new[0]
    old = (points[1], points[3])
    new = (0, h_w[0])
    x = ((lat_lon[1] - old[0]) * (new[1] - new[0]) / (old[1] - old[0])) + new[0]
    # y must be reversed because the orientation of the image in the matplotlib.
    # image - (0, 0) in upper left corner; coordinate system - (0, 0) in lower left corner
    return track_x + int(x), track_y + int(y)
    return track_x + int(x), track_y + h_w[1] - int(y)

gpx_file = open(args.gpxfile.name, 'r')
gpx = gpxpy.parse(gpx_file)

tmpdirname = tempfile.TemporaryDirectory(prefix='gpx', suffix=args.gpxfile.name)
print(tmpdirname)

context = staticmaps.Context()

if args.maptype == 'transparent':
    # background_image = Image.new("RGBA",(args.width,args.height), (0,0,0,0))
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

for track in gpx.tracks:
    for segment in track.segments:
        line = [staticmaps.create_latlng(p.latitude, p.longitude) for p in segment.points]
        context.add_object(staticmaps.Line(line))

image = context.render_cairo(args.width, args.height)
image.write_to_png("test.png")
