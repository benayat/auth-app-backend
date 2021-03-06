# imports: bcrypt for hashing the pasword before we upload it to the server,
# create_access_token from jwt, to create and send the jwt token,
# dateTime to time the token lifetime.
from database.db import db
from datetime import  datetime, timedelta
import re
from utils.time_to_gmt3 import get_local_time


# those enums will be lowerCase. will change if needed.
# ENUMS

# since flask-mongoengine doesn't support objectID neither LazyReferenceField, 
# and since and I must use a valid unique value for sender and receiver,
# I'll just add the objectID of owner and reciever as a stringField, and search in the controller when relevant.


class Message(db.Document):
    meta = {'collection': 'messages'}
    sender = db.EmailField(required=True, max_length=40)
    receiver = db.EmailField(required=True, max_length=50)
    message = db.StringField(required=True, max_length=100)
    subject = db.StringField(required=True, max_length=50)
    creation_date = db.DateTimeField(default=get_local_time(datetime.now()))
    was_message_read = db.BooleanField(default=False)

""" 
thoughts: 
- do I need a validation fot the BooleanField?does it support lowercase values like javaScript?

 """