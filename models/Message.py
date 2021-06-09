# imports: bcrypt for hashing the pasword before we upload it to the server,
# create_access_token from jwt, to create and send the jwt token,
# dateTime to time the token lifetime.
from database.db import db
from datetime import  datetime, timedelta
import re


# those enums will be lowerCase. will change if needed.
# ENUMS

# since flask-mongoengine doesn't support objectID neither LazyReferenceField, 
# and since and I must use a valid unique value for sender and receiver,
# I'll just add the objectID of owner and reciever as a stringField, and search in the controller when relevant.


class Message(db.Document):
    sender = db.StringField(required=True, min_length=12, max_length=12, regex = re.compile(r"/d+"))
    receiver = db.StringField(required=True, max_length=50)
    Message = db.EmailField(required=True, max_length=50)
    subject = db.StringField(required=True, max_length=30)
    creation_date = db.DateTimeField(required=True, default=datetime.utcnow)
    was_message_read = db.BooleanField(required=True, default=False)

""" 
thoughts: 
- do I need a validation fot the BooleanField?does it support lowercase values like javaScript?

 """