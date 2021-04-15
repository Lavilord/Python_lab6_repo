from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import copy
import json
from animal import Animal


with open("secret.json") as f:
    SECRET = json.load(f)

DB_URI = "mysql+pymysql://{user}:{password}@{host}:{port}/{db}".format(
    user=SECRET["user"],
    password=SECRET["password"],
    host=SECRET["host"],
    port=SECRET["port"],
    db=SECRET["db"])

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)


class AnimalModel(Animal, db.Model):
    id = db.Column(db.INTEGER, primary_key=True)
    weight_in_grams = db.Column(db.INTEGER, unique=False)
    price = db.Column(db.INTEGER, unique=False)
    origin_country = db.Column(db.String(64), unique=False)
    is_predator = db.Column(db.BOOLEAN, unique=False)
    eats_in_grams = db.Column(db.INTEGER, unique=False)

    def __init__(self, weight_in_grams, price, origin_country, is_predator, eats_in_grams):
        super().__init__(weight_in_grams, price, origin_country, is_predator, eats_in_grams)


class AnimalSchema(ma.Schema):
    class Meta:
        fields = ("weight_in_grams", "price", "origin_country", "is_predator", "eats_in_grams", "id")


animal_schema = AnimalSchema()
animals_schema = AnimalSchema(many=True)


@app.route("/animal", methods=["POST"])
def add_animal():
    deserialized_data = AnimalSchema().load(request.json)
    animal = AnimalModel(**deserialized_data)
    db.session.add(animal)
    db.session.commit()
    return animal_schema.jsonify(animal)


@app.route("/animal", methods=["GET"])
def get_all_animals():
    all_animals = AnimalModel.query.all()
    result = animals_schema.dump(all_animals)
    return jsonify({"animals": result})


@app.route("/animal/<id>", methods=["GET"])
def get_one_animal(id):
    animal = AnimalModel.query.get(id)
    if not animal:
        abort(404)
    return animal_schema.jsonify(animal)


@app.route("/animal/<id>", methods=["PUT"])
def update_animal(id):
    animal = AnimalModel.query.get(id)
    if not animal:
        abort(404)
    old_animal = copy.deepcopy(animal)
    deserialized_data = AnimalSchema().load(request.json)
    animal.weight_in_grams = deserialized_data["weight_in_grams"]
    animal.price = deserialized_data["price"]
    animal.origin_country = deserialized_data["origin_country"]
    animal.is_predator = deserialized_data["is_predator"]
    animal.eats_in_grams = deserialized_data["eats_in_grams"]
    db.session.commit()
    return animal_schema.jsonify(old_animal)


@app.route("/animal/<id>", methods=["DELETE"])
def delete_animal(id):
    animal = AnimalModel.query.get(id)
    if not animal:
        abort(404)
    db.session.delete(animal)
    db.session.commit()
    return animal_schema.jsonify(animal)


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)