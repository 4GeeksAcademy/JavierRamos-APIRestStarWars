import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, Users, Characters, Starships, Planets, FavoriteCharacters, FavoriteStarships, FavoritePlanets

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

#### USERS ####
@app.route('/users', methods=['GET'])
def get_all_users():
    all_users = Users.query.all()
    users_serialized = []
    for user in all_users:
        users_serialized.append(user.serialize())
    print(users_serialized)
    return jsonify({"data": users_serialized}), 200

@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    single_user = Users.query.get(id)
    if single_user is None:
        return jsonify({"msg": "User with id: {}, not found".format(id)}), 400
    return jsonify({"data": single_user.serialize()}), 200

@app.route('/user', methods=['POST'])
def create_user():
    data = request.json
    name = data.get('name')
    last_name = data.get('last_name')
    email = data.get('email')
    password = data.get('password')

    if not name or not last_name or not email or not password:
        return jsonify({"error": "All data are required."}), 400
    if Users.query.filter_by(email=email).first():
        return jsonify({"error": "User with this email already exists."}), 400
    
    new_user = Users(name=name, last_name=last_name, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"data": new_user.serialize()}), 201

#### CHARACTERS ####
@app.route('/characters', methods=['GET'])
def get_all_characters():
    all_characters = Characters.query.all()
    characters_serialized = []
    for character in all_characters:
        characters_serialized.append(character.serialize())
    print(characters_serialized)
    return jsonify({"data": characters_serialized}), 200

@app.route('/characters/<int:id>', methods=['GET'])
def get_character(id):
    single_character = Characters.query.get(id)
    if single_character is None:
        return jsonify({"msg": "Character with id: {}, not found".format(id)}), 400
    return jsonify({"data": single_character.serialize()}), 200

@app.route('/character', methods=['POST'])
def create_character():
    data = request.json
    name = data.get('name')
    heigth = data.get('heigth')
    mass = data.get('mass')
    hair_color = data.get('hair_color')
    eye_color = data.get('eye_color')
    skin_color = data.get('skin_color')
    birth_year = data.get('birth_year')
    gender = data.get('gender')
    
    if not name:
        return jsonify({"error": "Name is required."}), 400
    
    new_character = Characters(name=name, heigth=heigth, mass=mass, hair_color=hair_color, eye_color=eye_color, skin_color=skin_color, birth_year=birth_year, gender=gender)
    
    db.session.add(new_character)
    db.session.commit()
    
    return jsonify({"data": new_character.serialize()}), 201

#### PLANETS ####

@app.route('/planets', methods=['GET'])
def get_all_planets():
    all_planets = Planets.query.all()
    planets_serialized = []
    for planet in all_planets:
        planets_serialized.append(planet.serialize())
    print(planets_serialized)
    return jsonify({"data": planets_serialized}), 200

@app.route('/planets/<int:id>', methods=['GET'])
def get_planet(id):
    single_planet = Planets.query.get(id)
    if single_planet is None:
        return jsonify({"msg": "Planet with id: {}, not found".format(id)}), 400
    return jsonify({"data": single_planet.serialize()}), 200

@app.route('/planet', methods=['POST'])
def create_planet():
    data = request.json
    name = data.get('name')
    diameter = data.get('diameter')
    gravity = data.get('gravity')
    population = data.get('population')
    climate = data.get('climate')
    terrain = data.get('terrain')
    surface_water = data.get('surface_water')
    
    if not name:
        return jsonify({"error": "Name is required."}), 400
    
    new_planet = Planets(name=name, diameter=diameter, gravity=gravity, population=population, climate=climate, terrain=terrain, surface_water=surface_water)
    
    db.session.add(new_planet)
    db.session.commit()

    return jsonify({"data": new_planet.serialize()}), 201

#### FAVORITES ####
@app.route('/users/<int:id>/favorites')
def user_favorites(id):
    favorite_characters = db.session.query(FavoriteCharacters, Characters).join(Characters).filter(FavoriteCharacters.user_id == id).all()
    favorite_characters_serialized = []
    for favorite_character, character in favorite_characters:
        favorite_characters_serialized.append(character.serialize()["name"])

    favorite_planets = db.session.query(FavoritePlanets, Planets).join(Planets).filter(FavoritePlanets.user_id == id).all()
    favorite_planets_serialized = []
    for favorite_planet, planet in favorite_planets:
        favorite_planets_serialized.append(planet.serialize()["name"])
    
    return jsonify({"favorites": {"characters": favorite_characters_serialized, "planets": favorite_planets_serialized}}), 200

@app.route('/user/favorite/character', methods=['POST'])
def add_favorite_character():
    data = request.json
    user_id = data.get('user_id')
    character_id = data.get('character_id')
    
    if not user_id or not character_id:
        return jsonify({"error": "user_id and character_id are required."}), 400

    user = Users.query.get(user_id)
    if user is None:
        return jsonify({"msg": f'User with ID: {user_id}, not found'}), 404

    character = Characters.query.get(character_id)
    if character is None:
        return jsonify({"msg": f'Character with ID: {character_id}, not found.'}), 404
    
    new_favorite_character = FavoriteCharacters.query.filter_by(user_id=user_id, character_id=character_id).first()
    if new_favorite_character:
        return jsonify({"msg": "This character already exists in favorites for this user"}), 409
        
    new_favorite_character = FavoriteCharacters(user_id=user_id, character_id=character_id)
    
    db.session.add(new_favorite_character)
    db.session.commit()

    user_favorite_characters = db.session.query(FavoriteCharacters, Characters).join(Characters).filter(FavoriteCharacters.user_id == user_id).all()
    user_favorite_characters_serialized = []
    for user_favorite_character, character in user_favorite_characters:
        user_favorite_characters_serialized.append(character.serialize()["name"])

    return jsonify({"favorites": {"characters": user_favorite_characters_serialized}}), 201

@app.route('/user/favorite/planet', methods=['POST'])
def add_new_favorite_planet():
    data = request.json
    user_id = data.get('user_id')  
    planet_id = data.get('planet_id')

    if not user_id or not planet_id:
        return jsonify({"error": "user_id and planet_id are required."}), 400
    
    user = Users.query.get(user_id)
    if user is None:
        return jsonify({"msg": f'User with ID: {user_id}, not found'}), 404
    
    planet = Planets.query.get(planet_id)
    if planet is None:
        return jsonify({"msg": f'Planet with ID: {planet_id}, not found'}), 404
    
    new_favorite_planet = FavoritePlanets.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if new_favorite_planet:
        return jsonify({"msg": "This planet already exists in favorites for this user"}), 409
    
    new_favorite_planet = FavoritePlanets(user_id=user_id, planet_id=planet_id)
    print(new_favorite_planet)

    db.session.add(new_favorite_planet)
    db.session.commit()

    user_favorite_planets = db.session.query(FavoritePlanets, Planets).join(Planets).filter(FavoritePlanets.user_id == user_id).all()
    user_favorite_planets_serialized = []
    for user_favorite_planet, planets in user_favorite_planets:
        user_favorite_planets_serialized.append(planet.serialize()["name"])

    return jsonify({"msg": {"planets": user_favorite_planets_serialized}}), 201


@app.route('/user/<int:id>/favorite/character/<int:favorite_character_id>', methods=['DELETE'])
def delete_favorite_character(id, favorite_character_id):
    favorite_character_to_delete = FavoriteCharacters.query.filter_by(user_id=id, character_id=favorite_character_id).first()
    if favorite_character_to_delete is None:
        return jsonify({"msg": "Favorite Character not found"}), 404
    
    print(favorite_character_to_delete.serialize())
    try:
        db.session.delete(favorite_character_to_delete)
        db.session.commit()
        return jsonify({"msg": "Character deleted"}), 200
    except Exception as error:
        db.session.rollback()
        print(error)
        return jsonify({"msg": "An error occurred when deleting the favorite character"}), 500
    
@app.route('/user/<int:id>/favorite/planet/<int:favorite_planet_id>', methods=['DELETE'])
def delete_favorite_planet(id, favorite_planet_id):
    favorite_planet_to_delete = FavoritePlanets.query.filter_by(user_id=id, planet_id=favorite_planet_id).first()
    if favorite_planet_to_delete is None:
        return jsonify({"msg": "Favorite Planet not found"}), 404
    
    print(favorite_planet_to_delete.serialize())
    try:
        db.session.delete(favorite_planet_to_delete)
        db.session.commit()
        return jsonify({"msg": "Planet deleted"}), 200
    except Exception as error:
        db.session.rollback()
        print(error)
        return jsonify({"msg": "An error occurred when deleting the favorite planet"}), 500


if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)