import argparse
from gps_class import GPSVis
import gpxpy
import gpxpy.gpx
from PIL import Image, ImageDraw
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
                    default=8)
parser.add_argument('--trackcolor', choices=['red', 'green', 'blue'],
                    help='Color of the track',
                    default='blue')
parser.add_argument('--maptype', choices=['transparent', 'osm'],
                    help='Map style to use for the background',
                    default='transparent')
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

latitude_max = -99
latitude_min = 99
longitude_max = -99
longitude_min = 99

for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            if point.latitude > latitude_max:
                latitude_max = point.latitude
            if point.latitude < latitude_min:
                latitude_min = point.latitude
            if point.longitude > longitude_max:
                longitude_max = point.longitude
            if point.longitude < longitude_min:
                longitude_min = point.longitude

latitude_width = latitude_max - latitude_min
longitude_width = longitude_max - longitude_min

print((latitude_width, longitude_width))
if latitude_width < longitude_width:
    track_width = args.width * 0.9
    track_height = args.height * ((latitude_width*2)/longitude_width) * 0.9
    track_x = (args.width - track_width) / 2
    track_y = (args.height - track_height) / 2
else:
    track_height = args.height * 0.9
    track_width = args.width * (longitude_width/(latitude_width*2)) * 0.9
    track_x = (args.width - track_width) / 2
    track_y = (args.height - track_height) / 2
print ((track_width, track_height))

points = (latitude_min, longitude_min, latitude_max, longitude_max)

if args.maptype == 'transparent':
    background_image = Image.new("RGBA",(args.width,args.height), (0,0,0,0))
elif args.maptype == 'osm':
    sys.exit('not implemented yet')
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

img_points = []

for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            x1, y1 = scale_to_img((point.latitude, point.longitude), (track_x, track_y), (track_width, track_height), points)
            img_points.append((x1, y1))
            # print('Point at ({0},{1}) -> {2}'.format(point.latitude, point.longitude, point.elevation))

color=(0, 0, 255)
draw = ImageDraw.Draw(background_image)
draw.line(img_points, fill=color, width=args.trackwidth)

background_image.save('test.png', 'PNG')
