from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    last_name = db.Column(db.String(32))
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(32), nullable=False)
    user_favorite_characters = db.relationship("FavoriteCharacters", back_populates="user_id_relationship")
    user_favorite_planets = db.relationship("FavoritePlanets", back_populates="user_id_relationship")
    
    def __repr__(self):
        return f"User name: {self.name}"
    
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "last_name": self.last_name,
            "email": self.email
        }

class Characters(db.Model):
    __tablename__ = 'characters'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True)
    heigth = db.Column(db.Integer)
    mass = db.Column(db.Integer)
    hair_color = db.Column(db.String(20))
    eye_color = db.Column(db.String(20))
    skin_color = db.Column(db.String(20))
    birth_year = db.Column(db.String(20))
    gender = db.Column(db.String(20))
    favorite_characters = db.relationship("FavoriteCharacters", cascade="all, delete", back_populates="character_id_relationship")

    def __repr__(self):
        return f"Character name: {self.name}"
    
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "heigth": self.heigth,
            "mass": self.mass,
            "hair_color": self.hair_color,
            "eye_color": self.eye_color,
            "skin_color": self.skin_color,
            "birth_year": self.birth_year,
            "gender": self.gender
        }

class Planets(db.Model):
    __tablename__ = 'planets'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    diameter = db.Column(db.Integer)
    gravity = db.Column(db.String(50))
    population = db.Column(db.String(20))
    climate = db.Column(db.String(50))
    terrain = db.Column(db.String(50))
    surface_water = db.Column(db.String(20))
    favorite_planets = db.relationship("FavoritePlanets", cascade="all, delete", back_populates="planet_id_relationship")

    def __repr__(self):
        return f"Planet name: {self.name}"
    
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "diameter": self.diameter,
            "gravity": self.gravity,
            "population": self.population,
            "climate": self.climate,
            "terrain": self.terrain,
            "surface_water": self.surface_water
        }

class FavoriteCharacters(db.Model):
    __tablename__ = 'favorite_characters'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user_id_relationship = db.relationship("Users", back_populates="user_favorite_characters")
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'))
    character_id_relationship = db.relationship("Characters", back_populates="favorite_characters")

    def __repr__(self):
        return f"User: {self.user_id} -> likes character {self.character_id}"
    
    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "character_id": self.character_id
        }
    
class FavoritePlanets(db.Model):
    __tablename__ = 'favorite_planets'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user_id_relationship = db.relationship("Users", back_populates="user_favorite_planets")
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'))
    planet_id_relationship = db.relationship("Planets", back_populates="favorite_planets")

    def __repr__(self):
        return f"User: {self.user_id} -> likes planet: {self.planet_id}"
    
    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "planet_id": self.planet_id
        }