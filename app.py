from flask import Flask,request, send_file
import json
import os
import requests
import zipfile


app = Flask(__name__)


@app.route("/")
def home():
    return "In development"

@app.route("/osm2obj" , methods=['POST'])
def prueba():
    data = request.data
    print(data)
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


    return zip(parsed_data['name'])

@app.route("/test" , methods=['POST'])
def test():
    return send_file('kkkk.zip', mimetype='zip', attachment_filename="kkk.zip",as_attachment=True)

def osm_to_obj(coords):

    with open('polygone.poly','w') as f:
        f.write("polygone\n")
        for item in coords:
            f.write("\t"+str(item[0])+" "+str(item[1])+"\n")
        f.write('END')

    trim = r"""./osmconvert model.osm -B=polygone.poly -o=model2.osm"""
    # trim = r"""osmconvert.exe model.osm -B=polygone.poly -o=model2.osm"""
    os.system(trim)
    os.remove("model.osm")
    os.rename("model2.osm", "model.osm")
    convert = r"""java -Xmx512m -jar OSM2World/OSM2World.jar -i model.osm -o model3d.obj""" 
    os.system(convert)

    pass

def zip(name):
    os.rename("model3d.obj",name+".obj")
    os.rename("model3d.obj.mtl",name+".mtl")
    with zipfile.ZipFile(name+".zip",'w', zipfile.ZIP_DEFLATED) as zpf:
        zpf.write(name+".obj")
        zpf.write(name+".mtl")
    return send_file(name+".zip", mimetype='zip', attachment_filename=name+".zip", as_attachment=True)