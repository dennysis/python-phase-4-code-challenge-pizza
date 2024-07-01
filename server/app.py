from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, jsonify, make_response
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route("/")
def index():
    """
    Root endpoint of the API.

    Returns:
        str: A simple "Code challenge" message.

    Example:
        curl http://localhost:5555/
    """
    return "<h1>Code challenge</h1>"


@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    """
    Retrieve a list of all restaurants.

    Returns:
        list: A list of restaurant dictionaries, each containing the restaurant's id, name, and address.

    Example:
        curl http://localhost:5555/restaurants
    """
    restaurants = Restaurant.query.all()
    return [restaurant.to_dict(rules=['-restaurant_pizzas']) for restaurant in restaurants], 200


@app.route("/restaurants/<int:id>", methods=['GET', 'DELETE'])
def get_restaurant(id):
    """
    Retrieve a single restaurant by ID or delete a restaurant.

    Args:
        id (int): The ID of the restaurant to retrieve or delete.

    Returns:
        dict: A dictionary containing the restaurant's id, name, and address if GET, or an empty response if DELETE.
        int: A 404 error code if the restaurant is not found, or a 204 code if the restaurant is deleted.

    Example:
        curl http://localhost:5555/restaurants/1
        curl -X DELETE http://localhost:5555/restaurants/1
    """
    restaurant_by_id = Restaurant.query.filter(Restaurant.id == id).first()
    if not restaurant_by_id:
        return {"error": "Restaurant not found"}, 404
    
    if request.method == 'GET':
        return restaurant_by_id.to_dict(), 200
    elif request.method == 'DELETE':
        db.session.delete(restaurant_by_id)
        db.session.commit()
        return {}, 204


@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    """
    Retrieve a list of all pizzas.

    Returns:
        list: A list of pizza dictionaries, each containing the pizza's id, name, and description.

    Example:
        curl http://localhost:5555/pizzas
    """
    return [pizza.to_dict(rules=['-restaurant_pizzas']) for pizza in Pizza.query.all()], 200


@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    """
    Create a new restaurant-pizza association.

    Args:
        data (dict): A dictionary containing the price, pizza_id, and restaurant_id of the new association.

    Returns:
        dict: A dictionary containing the new association's id, price, pizza_id, and restaurant_id.
        int: A 201 code indicating the association was created successfully, or a 400 code if there were validation errors.

    Example:
        curl -X POST -H "Content-Type: application/json" -d '{"price": 10.99, "pizza_id": 1, "restaurant_id": 1}' http://localhost:5555/restaurant_pizzas
    """
    data = request.get_json()

    try:
        new_pizza = RestaurantPizza(
            price=data.get("price"),
            pizza_id=data.get("pizza_id"),
            restaurant_id=data.get("restaurant_id"),
        )
    except ValueError as e:
        return {"errors": ["validation errors"]}, 400 
    
    db.session.add(new_pizza)
    db.session.commit()

    return new_pizza.to_dict(), 201


if __name__ == "__main__":
    app.run(port=5555, debug=True)