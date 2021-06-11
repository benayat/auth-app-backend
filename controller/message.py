from flask import Response, Blueprint, request,jsonify
import json
from flask_jwt_extended import create_access_token, get_jwt, jwt_required,get_jwt_identity, set_access_cookies, unset_jwt_cookies, set_refresh_cookies
from datetime import timedelta, datetime, timezone
from models.Message import Message
from models.User import User
from mongoengine.errors import DoesNotExist, NotUniqueError, DoesNotExist, ValidationError, InvalidQueryError
from .errors import UnauthorizedError, errors
from mongoengine.queryset.visitor import Q
from bson import decode, encode


# created a blueprint for the user model, so I don't have to write all the endpoints inside the app.py main file.
messages = Blueprint('messages', __name__)

@messages.route('/write', methods=["POST"])
@jwt_required()
def write_message():
    try:
        sender = get_jwt_identity()
        body = request.get_json()
        print(body["sender"], sender)
        if(body["sender"]!=sender):
            print("problem!")
            raise UnauthorizedError
        message=Message(**body).save(force_insert=True)
        id=message.id
        return Response(json.dumps({'id':str(id)}),mimetype="application/json",status=201)
    except DoesNotExist as e:
        return Response(json.dumps(e.args), mimetype="application/json", status=404)
    except UnauthorizedError as e:
        return Response(json.dumps(errors), mimetype="application/json", status=401)
    except Exception as e:
        print(e)
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
        message = Message.objects(receiver=email, was_message_read=False).first()
        message.update(was_message_read=True)
        dict_message = message.to_mongo().to_dict()
        json_message = json.dumps(dict_message, default=str)
        return Response(json_message, mimetype="application/json", status=200)
    except Exception as e:
        return Response(json.dumps(e.args), mimetype="application/json", status=500)

@messages.route('/readall', methods=["GET"])
@jwt_required()
def read_all_unread_messages():
    try:
        print("reading new messages")
        email = get_jwt_identity()
        print(email)
        unread_messages = Message.objects(receiver=email, was_message_read=False)
        json_messages = [message.to_mongo().to_dict() for message in unread_messages]
        print(json_messages)
        unread_messages.update(was_message_read=True)
        
        return Response(json.dumps(json_messages, default=str),mimetype="application/json", status=200)
    except Exception as e:
        return Response(json.dumps(e.args), mimetype="application/json", status=500)

# simple delete function, based on the email, as a path param in the request. 
# since it's a sensitive action, it requires authentication.
# since ID is unique, I didn't bother to use first, I just deleted whatever result came out.
@messages.route('/delete/<id>',methods=["DELETE"])
@jwt_required()
def delete_message_by_id(id):
    try:
        email = get_jwt_identity()
        Message.objects(Q(id=id)&(Q(sender=email)|Q(receiver=email))).delete()
        return f'message {id} of {email} deleted successfully',200
    except DoesNotExist as e:
        return Response(json.dumps(e.args), mimetype="application/json", status=404)
    except Exception as e:
        return Response(json.dumps(e.args), mimetype="application/json", status=500)

# all we need to do is response the client to delete his cookie, thats all.


""" 
thoughts:
- update - only password should be updateable?
- accessing - do I even need the user Id if the email is unique? or just use the email?
- the message id is necessary, because it's the only way to distinguish a unique message.
 """
 