# GPXVideo

This script takes a GPS track from a GPX file and creates a video from it showing the track on a map. The map is taken from the OpenStreetmap project.

## Setup

Install prerequesites if needed, see the [Cairo Getting Started Guide](https://pycairo.readthedocs.io/en/latest/getting_started.html) for more information.

    # clone the repository
    git clone git@github.com:schneidr/GPXVideo.git
    # create a virtual environment
    python3 -m virtualenv GPXVideo
    cd GPXVideo
    # activate the virtual environment
    source bin/activate
    # install required python modules
    pip install -r requirements.txt

## Resources

- https://pypi.org/project/gpxpy/
- https://github.com/flopp/py-staticmaps
