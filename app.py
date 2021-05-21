from flask import Flask,request, send_from_directory
import json
import os
from ast import literal_eval
import requests

import flask
from flask.json import jsonify
from werkzeug.http import parse_date
from werkzeug.wrappers import response


app = Flask(__name__)

DOWNLOAD_DIRECTORY = "folder"

@app.route("/")
def home():
    return "In development"

@app.route("/osm2obj" , methods=['POST'])
def prueba():
    data = request.data
    parsed_data = json.loads(data.decode('utf-8').replace("'",'"'))
    
    coordsLat = parsed_data['coords']['lat']
    coordsLong = parsed_data['coords']['long']
    rectangleLat = parsed_data['rectangle']['lat']
    rectangleLong = parsed_data['rectangle']['long']
    
    coords = []
    rectangle = []

    for i in range(len(coordsLat)):
        coords.append([coordsLong[i],coordsLat[i]])
    for i in range(len(rectangleLat)):
        rectangle.append([rectangleLong[i],rectangleLat[i]])
    
    long = [item[0] for item in coords]
    lat = [item[1] for item in coords]
    max_long = max(long)
    max_lat = max(lat)
    min_long = min(long)
    min_lat = min(lat)
    URL= "https://api.openstreetmap.org/api/0.6/map?bbox=%s,%s,%s,%s" % (min_long,min_lat,max_long,max_lat)
    r = requests.get(URL)
    open('model.osm','wb').write(r.content)
    osm_to_obj(coords)

    return "wait"

def parse_obj(obj):
    for key in obj:
        if isinstance(obj[key], str):
            obj[key] = obj[key].encode('latin_1').decode('utf-8')
        elif isinstance(obj[key], list):
            obj[key] = list(map(lambda x: x if type(x) != str else x.encode('latin_1').decode('utf-8'), obj[key]))
        pass
    return obj

def osm_to_obj(coords):

    with open('polygone.poly','w') as f:
        f.write("polygone\n")
        for item in coords:
            f.write("\t"+str(item[0])+" "+str(item[1])+"\n")
        f.write('END')

    trim = r"""osmconvert model.osm -B=polygone.poly -o=model2.osm"""
    # trim = r"""osmconvert.exe model.osm -B=polygone.poly -o=model2.osm"""
    os.system(trim)
    os.remove("model.osm")
    os.rename("model2.osm", "model.osm")
    convert = r"""java -Xmx512m -jar OSM2World/OSM2World.jar -i model.osm -o model3d.obj""" 
    os.system(convert)

    pass