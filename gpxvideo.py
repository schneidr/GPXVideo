import argparse
import gpxpy
import gpxpy.gpx
import s2sphere
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

def write_image(points: list, filename: str, bounds: s2sphere.LatLngRect, args):
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

    context.add_bounds(bounds)
    context.add_object(staticmaps.Line(points))

    image = context.render_cairo(args.width, args.height)
    image.write_to_png(filename)

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
        points = []
        for point in segment.points:
            count += 1
            latlng = staticmaps.create_latlng(point.latitude, point.longitude)
            points.append(latlng)
            if count > 1:
                filename = "{0}/{1:06d}.png".format(tmpdir.name, count)
                print(filename)
                write_image(points, filename, bounds, args)
            
