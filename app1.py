from flask import Flask, render_template, request,jsonify
import json
import time
import requests
import geopy
from geopy.geocoders import Nominatim
import random
from math import sin, cos, sqrt, atan2, radians
import beepy as beep
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("pokemon-db.json")
firebase_admin.initialize_app(cred)
store = firestore.client()

url = "https://pokemon-go1.p.rapidapi.com/shiny_pokemon.json"

headers1 = {
    'x-rapidapi-key': "f2a42e970dmsh9f444138ec6fc80p1bdc5djsn6a5f8f18cfde",
    'x-rapidapi-host': "pokemon-go1.p.rapidapi.com"
    }

response1 = requests.request("GET", url, headers=headers1)

pokemon = []
pokemon_dit={}
pokemon=response1.content
l=len(pokemon)
pokemon_dit = json.loads(pokemon.decode('utf-8'))
print(type(pokemon_dit))
#print(pokemon)
#print(pokemon_dit)

url = "https://pokemon-go1.p.rapidapi.com/current_pokemon_moves.json"

headers2 = {
    'x-rapidapi-key': "f2a42e970dmsh9f444138ec6fc80p1bdc5djsn6a5f8f18cfde",
    'x-rapidapi-host': "pokemon-go1.p.rapidapi.com"
    }

response2 = requests.request("GET", url, headers=headers2)

pokemon_moves = []
pokemon_moves = response2.content
print(type(pokemon_moves))
#n = len(pokemon_moves)
pokemon_moves = json.loads(pokemon_moves.decode('utf-8'))
print(type(pokemon_moves))
#rint(pokemon_moves)


places=["Malad","Andheri","Churchgate","Dahisar","Vile Parle","Ashok Nagar","Asha Nagar","Borivali"
,"Navi Mumbai","Panvel","Powai"]


'''for key,value in pokemon_dit.items():
    address = random.choice(places)
    geolocator = Nominatim(user_agent=".")
    location = geolocator.geocode(address)
    plat = location.latitude
    plong = location.longitude
    value['lat'] = plat
    value['long'] = plong'''
    

R = 6373.0

app = Flask(__name__)
count=1

@app.route('/catch',methods=['GET','POST'])
def catch_pokemon():
    print(f"The method is {request.method}")
    if request.method == "POST":
        name = request.form["pokemon"]
        for key,value in pokemon_dit.items():
            if name == value['name']:
                # frequency = 500  
                # duration = 500
                # for i in range(4):
                #     winsound.Beep(frequency,duration)
                #     time.sleep(1)

                return {"Message":"Congratulations!! pokemon found"}
                break

            else:
                return {"message":"Pokemon not found"}
            

    return render_template("pokemon.html")



# @app.route('/read',methods=['GET'])
# def read_data():
#     for key,value in pokemon_dit.items():
#         address = random.choice(places)
#         geolocator = Nominatim(user_agent=".")
#         location = geolocator.geocode(address)
#         plat = location.latitude
#         plong = location.longitude
#         value['lat'] = plat
#         value['long'] = plong
#     return jsonify(pokemon_dit)


@app.route('/addPokemon',methods = ['GET','POST'])
def add():
    with open("poke.json","r") as log:
        pokemon_dit = json.load(log)
    for key, values in pokemon_dit.items():
        store.collection("POKEMONS").add(values)
    return {}

@app.route('/hunt',methods=['GET','POST'])
def hunt_poke():
    docs = store.collection("DETECTED-POKE").stream()

    for doc in docs:
        doc.reference.delete()

    pokemon_lst=[]
    dit={}
    print(f"the method is {request.method}")
    if request.method == "POST":
        address = request.form["location"]
        r = 5
        geolocator = Nominatim(user_agent=".")
        location = geolocator.geocode(address)
        lat = location.latitude
        longit = location.longitude
        with open("poke.json",'r') as logs:
            logdata = json.load(logs)

            
        # for key,value in logdata.items():
        #     lat1 = radians(lat)
        #     lon1 = radians(longit)
        #     lat2 = radians(value["lat"])
        #     lon2 = radians(value["long"])

        docs = store.collection("POKEMONS").stream()
        for doc in docs:
            lat1 =  radians(lat)
            lon1 = radians(longit)
            lat2 = radians(doc.to_dict().get("lat"))
            lon2 = radians(doc.to_dict().get("long"))

            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = (sin(dlat/2))**2 + cos(lat1) * cos(lat2) * (sin(dlon/2))**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            proximity = R * c

            if proximity <= r:
                #print(proximity)
                pokemon_lst.append(doc.to_dict())

        l1 = len(pokemon_lst)
        #dit = dict(pokemon_lst)
        if l1<1:
            return {"message":"No pokemon found near you"}

        else:
            for i in range(3):
                beep.beep(1)
            #print(pokemon_lst)
            # with open("catch.json",'w') as logs:
            #     logs.write(json.dumps(pokemon_lst))
            #return(dit)
            for items in pokemon_lst:
                store.collection("DETECTED-POKE").add(items)
            
    return render_template("hunt.html",POKEMON = pokemon_lst)
               
@app.route('/pokeball',methods=['GET','POST'])
def catch():
    print(f"The method is{request.method}")
    pokelst=[]
    pokedit = {}
    if request.method == 'GET':
        dit={}
        # with open("catch.json",'r') as logs:
        #     logdata = json.load(logs)
        docs =store.collection("DETECTED-POKE").stream()

        for doc in docs:
            dit = doc.to_dict()
            pokelst.append(dit)
        pokedit = random.choice(pokelst)
        #global count
            #count+=1
            # with open("mypokemon.json",'r') as poke:
            #     pokedata = json.load(poke)
            #     pokedata["poke_data"][count] = dit
            # with open("mypokemon.json",'w') as poke:
            #     poke.write(json.dumps(pokedata))

        store.collection("MYPOKEMON").add(pokedit)

        for items in pokemon_moves:
            if pokedit["name"] == items["pokemon_name"]:
                dit = items
                store.collection("MYPOKEMOVE").add(dit)
                break      
    
            
            #return {"message":"Pokemon caught successfully, check your pokemon deck"}
    
    return {"message":"Pokemon caught successfully, check your pokemon deck"}

# @app.route('/flushall',methods=['GET','POST'])
# def clear():
#     docs = store.collection("DETECTED-POKE").stream()

#     for doc in docs:
#         doc.reference.delete()


# @app.route('/viewmoves',methods = ['GET','POST'])
# def moves():
#     docs = store.collection("MYPOKEMON").stream()
#     for doc in docs:    
#         for items in pokemon_moves:
#             if doc.to_dict().get("name") == items["pokemon_name"]:
#                 dit = items
#                 store.collection("MYPOKEMOVE").add(dit)
#                 break      
    
#     return {"message":"You may check your pokemon moves now"}


if __name__ == '__main__':
    app.run(host="127.0.0.1",port="5000",debug=False)
