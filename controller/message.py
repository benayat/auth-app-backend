from flask import Response, Blueprint, request,jsonify
import json
from flask_jwt_extended import create_access_token, get_jwt, jwt_required,get_jwt_identity, set_access_cookies, unset_jwt_cookies, set_refresh_cookies
from datetime import timedelta, datetime, timezone
from models.Message import Message
from models.User import User
from mongoengine.errors import DoesNotExist, NotUniqueError, DoesNotExist, ValidationError, InvalidQueryError
from .errors import UnauthorizedError
from mongoengine.queryset.visitor import Q
# created a blueprint for the user model, so I don't have to write all the endpoints inside the app.py main file.
messages = Blueprint('messages', __name__)


# @messages.route("/")
# def hellow():
#     return ("hellow")
# routs decorators and functions:
# each route has it's endpoint, allowed methods, and possible decorators. for example - jwt required.
# this route is for getting all the users. since it should be only for admins, I didn't give it any auth yet.
# custom exceptions: DoesNotExist if the db is empty, which will return 404 to the user.

@messages.route('/write', methods=["POST"])
@jwt_required()
def write_message():
    try:
        body = request.get_json()
        message=Message(**body).save(force_insert=True)
        id=message.id
        return Response(json.dumps({'id':str(id)}),mimetype="application/json",status=201)
    except DoesNotExist as e:
        return Response(json.dumps(e.args), mimetype="application/json", status=404)
    except Exception as e:
        return Response(json.dumps(e.args), mimetype="application/json", status=500)

@messages.route('/allmessages',methods=["GET"])
@jwt_required()
def get_all_messages_of_user():
    try:
        identity= get_jwt_identity()
        messages = Message.objects(Q(sender=identity)|Q(receiver=identity)).to_json()
        if not messages:
            raise DoesNotExist
        return Response(messages,mimetype="application/json", status=200)
    except DoesNotExist as e:
        return Response(json.dumps(e.args), mimetype="application/json", status=404)
    except Exception as e:
        return Response(json.dumps(e.args), mimetype="application/json", status=500)

@messages.route('/readone', methods=["GET"])
@jwt_required()
def read_last_unread_message():
    try:
        print("reading new message")
        email = get_jwt_identity()
        print(email)
        message = Message.objects.exclude('id').first(email=email, was_message_read=False).to_json()
        print(message)
        return Response(message,mimetype="application/json", status=200)
    except Exception as e:
        return Response(json.dumps(e.args), mimetype="application/json", status=500)

@messages.route('/readall', methods=["GET"])
@jwt_required()
def read_all_unread_messages():
    try:
        print("reading new message")
        email = get_jwt_identity()
        print(email)
        unread_messages = Message.objects(email=email, was_message_read=False).to_json()
        unread_messages.update(was_message_read=True)
        print(unread_messages)
        return Response(unread_messages,mimetype="application/json", status=200)
    except Exception as e:
        return Response(json.dumps(e.args), mimetype="application/json", status=500)

# simple delete function, based on the email, as a path param in the request. 
# since it's a sensitive action, it requires authentication.
# plan to improve: need to get current user's details, so only the specified user can delete his account, and not anyone.
# for that I'll use get_jwt_identity, very soon.
@messages.route('/delete/<id>',methods=["DELETE"])
@jwt_required()
def delete_message_by_id(id):
    try:
        email = get_jwt_identity()
        Message.objects.first(Q(id=id)|(Q(sender=email)|Q(receiver=email))).delete()
        return f'message deleted {email} deleted successfully',200
    except DoesNotExist as e:
        return Response(json.dumps(e.args), mimetype="application/json", status=404)
    except Exception as e:
        return Response(json.dumps(e.args), mimetype="application/json", status=500)

# all we need to do is response the client to delete his cookie, thats all.


""" 
thoughts:
- update - only password should be updateable?
- accessing - do I even need the Id if the email is unique? or just use the email?
 """
 