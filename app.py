
import os
from datetime import timedelta
from flask.wrappers import Response
# considering just raising the exception in the blueprint/view file, and then return the response here,
# since it's almost the same code. on the other hand - I don't want to burden the app.py file, so I'm not sure.
# from werkzeug.exceptions import HTTPException
from flask_cors import CORS
from flask import Flask
from database.db import initialize_db
from flask_jwt_extended import JWTManager
from controller.user import users
from controller.message import messages
# if I compare it to express, it's just like importing a router into the app.js file.
# next steps: initializing the flask app, binding it to jwt manager, giving it the connection string to mongodb,
# initializing the database with initialize_db function from db. file, and lastly,
# registering the user blueprint I made earlier. 
app=Flask(__name__)
CORS(app)
# configuring the app from an env file.
# app.config.from_envvar('ENV_FILE_LOCATION')

jwt = JWTManager(app)
app.config['JWT_TOKEN_LOCATION'] = 'cookies'
app.config['JWT_ACCESS_COOKIE_PATH'] = '/api/'
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
# for production - to change everything to https:
# app.config['JWT_COOKIE_SECURE'] = False

app.config['MONGODB_SETTINGS'] = {
    'db': 'moviesDB',
    'host': "mongodb+srv://benayat:fmWAK3TLrJwHxr8@cluster0.ptwdq.mongodb.net/authDB?retryWrites=true&w=majority",
    # 'host': 'mongodb://localhost/database_name'
}
initialize_db(app)
@app.route('/',methods=["GET"])
def hello():
    return "hellow there!",200
app.register_blueprint(users,url_prefix='/api/users')
app.register_blueprint(messages,url_prefix='/api/messages')
app.run(debug=True)

# to sum it up: all the blueprint does is just to import sub-routers into the app.
