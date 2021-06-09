# imports: bcrypt for hashing the pasword before we upload it to the server,
# create_access_token from jwt, to create and send the jwt token,
# dateTime to time the token lifetime.
from database.db import db
import bcrypt
from flask_jwt_extended import create_access_token
from datetime import  timedelta
# those enums will be lowerCase. will change if needed.
# ENUMS
GENDER = ("male", "female")
MEDICAL_CONDITIONS = ("poor", "bellow average", "average", "above average")

class User(db.Document):
    firstName = db.StringField(required=True, max_length=20)
    lastName = db.StringField(required=True, max_length=30)
    email = db.EmailField(required=True, max_length=40, unique=True)
    password = db.StringField(required=True)
    age = db.IntField(required=True, max_length=3)
    gender = db.StringField(max_length=6, choices=GENDER)
    medicalCondition = db.StringField(required=True, choises=MEDICAL_CONDITIONS)
    @staticmethod
    def encryptPassword(userRaw):
        salt = bcrypt.gensalt(rounds=8)
        encoded = userRaw["password"].encode('utf-8')
        password = bcrypt.hashpw(encoded, salt)
        return password
    @staticmethod
    def generateAuthToken(email):
        return create_access_token(identity=str(email))
  
    def check_password(self , rawPassword):
        return bcrypt.checkpw(rawPassword.encode('utf-8'), self.password.encode('utf-8'))
        

""" 
thoughts: 
- do I even need a name? or maybe not? 

 """