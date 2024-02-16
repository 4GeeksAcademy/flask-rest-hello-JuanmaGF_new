"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planets, Favorites
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)
# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code
# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def get_user():
    users = User.query.all()
    print(users)
    all_users = list(map(lambda x: x.serialize(), users))
    print(all_users)
    return jsonify(all_users)

@app.route('/people', methods=['GET'])
def get_people():
    peoples = People.query.all()
    all_people = list(map(lambda x: x.serialize(), peoples))
    return jsonify(all_people), 200 

@app.route('/people/<int:people_id>', methods=['GET'])
def get_people_id(people_id):
    people = People.query.get(people_id)
    if people:
        return jsonify(people.serialize()), 200
    else:
        return jsonify({"error": "People not found"}), 404

@app.route('/planets', methods=['GET'])
def get_planet():
    planetas = Planets.query.all()
    all_planet = list(map(lambda x: x.serialize(), planetas))
    return jsonify(all_planet), 200 

@app.route('/planets/<int:planets_id>', methods=['GET'])
def get_planet_id(planets_id):
    planet = Planets.query.get(planets_id)
    if planet:
        return jsonify(planet.serialize()), 200
    else:
        return jsonify({"error": "Planet not found"}), 404
    
@app.route('/user/favorites', methods=['GET'])
def get_favorites():
    favorite = Favorites.query.all()
    all_favorites = list(map(lambda x: x.serialize(), favorite))
    return jsonify(all_favorites), 200 


@app.route('/favorites/planets/<int:planet_id>', methods=['POST'])
def create_favorites_planets(planet_id):
    body = request.get_json()
    new_planet = Planets(
        id=body.get('id'),
        name=body.get('name'),
        climate=body.get('climate'),
        terrain=body.get('terrain'),
        population=body.get('population')
    )

    db.session.add(new_planet)
    db.session.commit()

    return jsonify(new_planet.serialize()), 200

@app.route('/favorites/people/<int:people_id>', methods=['POST'])
def create_favorites_people(people_id):
    body = request.get_json()
    new_people = People(
        id=body.get('id'),
        name=body.get('name'),
        birth_year=body.get('birth_year'),
        eye_color=body.get('eye_color'),
        height=body.get('height'),
        mass=body.get('mass'),
        skin_color=body.get('skin_color'),
        hair_color=body.get('hair_color')
       
    )

    db.session.add(new_people)
    db.session.commit()

    return jsonify(new_people.serialize()), 200

@app.route('/user', methods=['POST'])
def create_user():
    request_body_user = request.get_json()

    new_user = User(first_name=request_body_user["first_name"], last_name=request_body_user["last_name"], email=request_body_user["email"], password=request_body_user["password"])
    db.session.add(new_user)
    db.session.commit()

    return jsonify(request_body_user), 200 

@app.route('/favorites/people/<int:people_id>', methods=['DELETE'])
def delete_favorites_people(people_id):
    people_to_delete = People.query.get(people_id)

    if people_to_delete:
        db.session.delete(people_to_delete)
        db.session.commit()
        return jsonify({"message": "People deleted successfully"}), 200
    else:
        return jsonify({"error": "People not found"}), 404
    

@app.route('/favorites/planets/<int:planets_id>', methods=['DELETE'])
def delete_favorites_planets(planets_id):
    planets_to_delete = Planets.query.get(planets_id)

    if planets_to_delete:
        db.session.delete(planets_to_delete)
        db.session.commit()
        return jsonify({"message": "Planet deleted successfully"}), 200
    else:
        return jsonify({"error": "Planet not found"}), 404
    
# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)