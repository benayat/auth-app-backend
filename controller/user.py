""" 
imports: I used json to convert a dict to json for the responsed, with json.dumps method.
- jwt_required to verify user token for the auth actions.
- timedelta for limiting the token life time. for now it's 7 days, but it can change acording to the needs of security.
- imported the user model I made.
- imported the manual errors I made earlier. considering removing the error file, make it all happen here.

 """

from flask import Response, Blueprint, request,jsonify
import json
from flask_jwt_extended import create_access_token, get_jwt, jwt_required,get_jwt_identity, set_access_cookies, unset_jwt_cookies, set_refresh_cookies
from datetime import timedelta, datetime, timezone

from models.User import User
from mongoengine.errors import DoesNotExist, NotUniqueError, DoesNotExist, ValidationError, InvalidQueryError
from .errors import UnauthorizedError

# created a blueprint for the user model, so I don't have to write all the endpoints inside the app.py main file.
users = Blueprint('users', __name__)

# Using an `after_request` callback, we refresh any token that is within 30
# minutes of expiring. Change the timedeltas to match the needs of your application.
# source for this function: https://flask-jwt-extended.readthedocs.io/en/stable/refreshing_tokens/
@users.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original respone
        return response


# @users.route("/")
# def hellow():
#     return ("hellow")
# routs decorators and functions:
# each route has it's endpoint, allowed methods, and possible decorators. for example - jwt required.
# this route is for getting all the users. since it should be only for admins, I didn't give it any auth yet.
# custom exceptions: DoesNotExist if the db is empty, which will return 404 to the user.
# @users.route('/allusers',methods=["GET"])
# @jwt_required()
# def get_users():
#     try:
#         # print("getting all users")
#         users=User.objects().to_json()
#         if not users:
#             raise DoesNotExist
#         return Response(users,mimetype="application/json", status=200)
#     except DoesNotExist as e:
#         return Response(json.dumps(e.args), mimetype="application/json", status=404)
#     except Exception as e:
#         return Response(json.dumps(e.args), mimetype="application/json", status=404)


        
# I prefer to use the Response class, but since it can't return many types as data, 
# I'll just serialize the dictionary to a json string with json.dumps.
# sign up route. getting the user from the request body as json, hashing the password, and then uploading to the mongo db collection.
# custom exceptions: NotUniqueError if the user email exists already, since the email is unique.
@users.route("/signup", methods=["POST"])
def sign_up():
    try:
        body = request.get_json()
        body["password"]=User.encryptPassword(body)
        print(body["password"])
        user=User(**body).save(force_insert=True)
        id=user.id
        print(str(id))
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
        print(user)
        if user.check_password(body["password"]):
            print("pasword is ok!")
            access_token = User.generateAuthToken(email)
            dict_user=json.loads(user)
            dict_user.pop("password",None)
            response = jsonify({"user":dict_user})
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
# plan to improve: need to get current user's details, so only the specified user can delete his account, and not anyone.
# for that I'll use get_jwt_identity, very soon.
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

@users.route("/logout", methods=["GET"])
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
 