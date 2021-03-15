import os
from re import S
from flask import Flask, request, jsonify, abort
from flask.globals import session
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)
dbsession = session()
# '''
# @TODO uncomment the following line to initialize the datbase
# !! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
# !! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
# '''

# db_drop_and_create_all()

## ROUTES
@app.route('/drinks')
def get_drinks():
    return jsonify({
        "success": True, "drinks":[drink.short() for drink in Drink.query.all()]
    })


@app.route('/drinks-detail')
@requires_auth(permission='get:drinks-detail')
def get_detailed_drinks(_):
    return jsonify({
        "success": True, "drinks":[drink.long() for drink in Drink.query.all()]
    })


@app.route('/drinks', methods=['POST'])
@requires_auth(permission='post:drinks')
def create_drink(_):
    body = request.get_json()
    title = body.get('title', None)
    recipe = body.get('recipe', None)
    drink = Drink()
    drink.title = title
    drink.recipe = json.dumps(recipe)

    drink.insert()
    
    return jsonify({
        "success": True, 
        "drinks": drink.long()
        })


@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth(permission='patch:drinks')
def edit_drink(_, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()

    if drink is None:
        AuthError(404, 404)
    
    body = request.get_json()

    drink.title = body.get('title', None)
    drink.recipe = json.dumps(body.get('recipe', None))

    dbsession.commit()

    return jsonify({
        "success": True, 
        "drinks": drink.long()
        })


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth(permission='delete:drinks')
def delete_drink(id):
    drink = Drink.query.filter(Drink.id == id).one_none()

    if drink is None:
        AuthError(404, 404)

    drink.delete()

    return jsonify({"success": True, "delete": id})

## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422


@app.errorhandler(404)
def resource_not_found(error):
    return  jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''


@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response