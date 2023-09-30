#!/usr/bin/python3
"""handles all RESTful API actions for `Place`"""
from flask import jsonify, abort, request

from api.v1.views import app_views
from models import storage
from models.city import City
from models.place import Place
from models.user import User
from models.state import State


@app_views.route("/cities/<city_id>/places")
def places(city_id):
    """Get all places in a city

    Args:
        city_id (str): ID of the City

    Returns:
        list: All the places in that city

    Raises:
        404: If the specified city_id does not exist
    """
    city = storage.get(City, city_id)
    if not city:
        abort(404)
    result = []

    for place in city.places:
        result.append(place.to_dict())

    return jsonify(result)


@app_views.route("/places/<place_id>")
def place(place_id):
    """Get a place

    Args:
        place_id (str): ID of the place

    Returns:
        dict: Place JSON

    Raises:
        404: If the specified place_id does not exist
    """
    place = storage.get(Place, place_id)
    if not place:
        abort(404)

    return jsonify(place.to_dict())


@app_views.route("/places/<place_id>", methods=["DELETE"])
def delete_place(place_id):
    """Delete a place

    Args:
        place_id (str): ID of the place

    Returns:
        dict: An empty JSON

    Raises:
        404: If the specified place_id does not exist
    """
    place = storage.get(Place, place_id)
    if not place:
        abort(404)

    place.delete()
    storage.save()

    return jsonify(place.to_dict())


@app_views.route("/cities/<city_id>/places", methods=["POST"])
def create_place(city_id):
    """Create a places in a city.

    Args:
        city_id (str): ID of the City where the place will be created.

    Returns:
        dict: The created place.

    Raises:
        404: If the specified city_id does not exist.
        400: If the request body is not a valid JSON or if it is missing the
             user_id or name.
    """
    payload = request.get_json()
    city = storage.get(City, city_id)
    if not city:
        abort(404)
    if not payload:
        abort(400, "Not a JSON")
    if "user_id" not in payload:
        abort(400, "Missing user_id")
    if not storage.get(User, payload["user_id"]):
        abort(404)
    if "name" not in payload:
        abort(400, "Missing name")

    place = Place(city_id=city_id, **payload)
    place.save()

    return jsonify(place.to_dict()), 201


@app_views.route("/places/<place_id>", methods=["PUT"])
def update_place(place_id):
    """Update a place.

    Args:
        place_id (str): ID of the place to update.

    Returns:
        dict: Updated place in JSON.

    Raises:
        404: If the specified place_id does not exist.
        400: If the request body is not a valid JSON.
    """
    place = storage.get(Place, place_id)
    payload = request.get_json()
    if not place:
        abort(404)
    if not payload:
        abort(400, "Not a JSON")

    for key, value in place.to_dict().items():
        if key not in [
            "id",
            "user_id",
            "city_id",
            "created_at",
            "updated_at",
            "__class__",
        ]:
            setattr(place, key, payload[key] if key in payload else value)
    place.save()

    return jsonify(place.to_dict())
