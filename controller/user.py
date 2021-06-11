""" 
imports: I used json to convert a dict to json for the response, with json.dumps method.
- jwt_required to verify user token for the auth actions.
- timedelta for limiting the token's life time. for now it's one hour, but it can change acording to the needs of security.
- imported the user model I made.
- imported the manual errors I made earlier. considering removing the error file, make it all happen here.

 """

from flask import Response, Blueprint, request,jsonify
import json
from flask_jwt_extended import create_access_token, get_jwt, jwt_required,get_jwt_identity, set_access_cookies, unset_jwt_cookies, set_refresh_cookies
from datetime import timedelta, datetime, timezone
from utils.time_to_gmt3 import get_local_time
from models.User import User
from mongoengine.errors import DoesNotExist, NotUniqueError, DoesNotExist, ValidationError, InvalidQueryError
from .errors import UnauthorizedError

# created a blueprint for the user model, so I don't have to write all the endpoints inside the app.py main file.
users = Blueprint('users', __name__)

# Using an `after_request` callback, we refresh any token that is within 30
# minutes of expiring.
# source in the docs: https://flask-jwt-extended.readthedocs.io/en/stable/refreshing_tokens/
# since I added the utils package=>time_to_gmt3=>get_local_time function, I changed all messages create time to local israel time, 
# so I need to change the time here as well.
@users.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = get_local_time(datetime.now(timezone.utc))
        print(now)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original respone
        return response
        
# I prefer to use the Response class, but since it can't return many types as data, 
# I'll just serialize the dictionary to a json string with json.dumps.
# sign up route. getting the user from the request body as json, hashing the password, and then uploading to the mongo db collection.
# custom exceptions: NotUniqueError if the user email exists already, since the email is unique.
@users.route("/signup", methods=["POST"])
def sign_up():
    try:
        body = request.get_json()
        body["password"]=User.encryptPassword(body)
        user=User(**body).save(force_insert=True)
        id=user.id
        return Response(json.dumps({'id':str(id)}),mimetype="application/json",status=201)
    except NotUniqueError as e:
        return Response(json.dumps(e.args), mimetype="application/json", status=400)
    except Exception as e:
        return Response(json.dumps(e.args), mimetype="application/json", status=500)

# I'll use this function as an example for the current error handling: 
# first is try and except, and I raise a specific error if necessary. 
# in the except block I handle the error, usually return the relevant Response instance, with the relevant status code.
# login: verify the user credentials and then give him back a new jwt token, valid for certain time.
# exceptions: UnauthorizedError if the user couldn't identify correctly.
@users.route("/login", methods=["POST"])
def login():
    try:
        body=request.get_json()
        email=body.get('email')
        user = User.objects.get(email=email)
        if user.check_password(body["password"]):
            print("pasword is ok!")
            access_token = User.generateAuthToken(email)
            name=user.first_name+" "+user.last_name
            response = jsonify({"user":name, "id": str(user.id)})
            set_access_cookies(response, access_token)
            return response, 200
        else:
            raise UnauthorizedError
    except UnauthorizedError as e:
        return Response(json.dumps(e.args), mimetype="application/json", status=401)
    except Exception as e:
        return Response(json.dumps(e.args), mimetype="application/json", status=500)

# updating the password.
# the email comes as a path params, and in the req.body we have the new password with key-value json format.

@users.route("/update_password",methods=["PUT"])
@jwt_required()
def update_password():
    try:
        body=request.get_json()
        email = get_jwt_identity()
        print(email)
        User.objects.get(email=email).update(**body)
        return 'updated successfuly', 200
    except InvalidQueryError as e:
        return Response(json.dumps(e.args), mimetype="application/json", status=401)
    except DoesNotExist as e:
        return Response(json.dumps(e.args), mimetype="application/json", status=404)
    except Exception as e:
        return Response(json.dumps(e.args), mimetype="application/json", status=500)

@users.route('/me', methods=["GET"])
@jwt_required()
def get_user():
    try:
        print("getting one user")
        email = get_jwt_identity()
        print(email)
        user = User.objects.exclude('id').exclude('password').get(email=email).to_json()
        print(user)
        return Response(user,mimetype="application/json", status=200)
    except Exception as e:
        return Response(json.dumps(e.args), mimetype="application/json", status=500)

# simple delete function, based on the email, as a path param in the request. 
# since it's a sensitive action, it requires authentication.
# plan to improve: need to get current user's location, with jwt_location and use it as an extra layer of security.

# I decided to keep all messages in the archive, even after user is deleted, especially because 
# there could be other users who still depend on it.

@users.route('/delete',methods=["DELETE"])
@jwt_required()
def delete_user():
    try:
        email = get_jwt_identity()
        User.objects.get(email=email).delete()
        return f'user with email {email} deleted successfully',200
    except DoesNotExist as e:
        return Response(json.dumps(e.args), mimetype="application/json", status=404)
    except Exception as e:
        return Response(json.dumps(e.args), mimetype="application/json", status=500)

# all we need to do is response the client to delete his cookie, thats all.

@users.route("/logout", methods=["PUT"])
@jwt_required()
def logout():
    try:
        resp = jsonify(msg = "Successfully logged out")
        unset_jwt_cookies(resp)
        return resp, 200
    except Exception as e:
        return Response(json.dumps(e.args), mimetype="application/json", status=500)

""" 
thoughts:
- update - only password should be updateable?
- accessing - do I even need the Id if the email is unique? or just use the email?
 """
 