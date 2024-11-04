#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route('/campers', methods=["GET", "POST"])
def all_campers():
    if request.method == "GET":
        campers = Camper.query.all()
        response_body = [camper.to_dict(rules=('-signups',)) for camper in campers]
        return make_response(response_body, 200)
    
    elif request.method == "POST":
        name_data = request.json.get('name')
        age_data = request.json.get('age')
        try:
            new_camper = Camper(name=name_data, age=age_data)
            db.session.add(new_camper)
            db.session.commit()
            response_body = new_camper.to_dict(rules=('-signups',))
            return make_response(response_body, 201)
        except:
            response_body = {
                "errors": ["validation errors"]
            }
            return make_response(response_body, 400)

@app.route('/campers/<int:id>', methods=["GET", "PATCH"])
def camper_by_id(id):
    camper = db.session.get(Camper, id)

    if camper:
        if request.method == "GET":
            response_body = camper.to_dict(rules=('-signups.camper', '-signups.activity.signups'))
            return make_response(response_body, 200)

        elif request.method == "PATCH":
            try:
                for attr in request.json:
                    setattr(camper, attr, request.json.get(attr))
                db.session.commit()
                response_body = camper.to_dict(rules=('-signups',))
                return make_response(response_body, 202)

            except:
                response_body = {
                    "errors": ["validation errors"]
                }
                return make_response(response_body, 400)

    else:
        response_body = {
            "error": "Camper not found"
        }
        return make_response(response_body, 404)
    
@app.route('/activities')
def all_activities():
    activities = Activity.query.all()
    response_body = [activity.to_dict(rules=('-signups',)) for activity in activities]
    return make_response(response_body, 200)

@app.route('/activities/<int:id>', methods=["DELETE"])
def activity_by_id(id):
    activity = db.session.get(Activity, id)

    if activity:
        db.session.delete(activity)
        db.session.commit()
        return make_response({}, 204)

    else:
        response_body = {
            "error": "Activity not found"
        }
        return make_response(response_body, 404)
    
@app.route('/signups', methods=["POST"])
def all_signups():
    time_data = request.json.get('time')
    camper_id_data = request.json.get('camper_id')
    activity_id_data = request.json.get('activity_id')
    try:
        new_signup = Signup(time=time_data, camper_id=camper_id_data, activity_id=activity_id_data)
        db.session.add(new_signup)
        db.session.commit()
        response_body = new_signup.to_dict(rules=('-activity.signups', '-camper.signups'))
        return make_response(response_body, 201)
    
    except:
        response_body = {
            "errors": ["validation errors"]
        }
        return make_response(response_body, 400)

@app.route('/')
def home():
    return ''

if __name__ == '__main__':
    app.run(port=5555, debug=True)
