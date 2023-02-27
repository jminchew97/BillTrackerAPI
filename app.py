from flask import Flask, request, render_template, redirect, url_for, make_response, jsonify
from werkzeug.security import check_password_hash
from database_api import BillDBAPI
from data_handler import *
import uuid
from datetime import date

from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from flask_jwt_extended import set_access_cookies
from flask_jwt_extended import unset_jwt_cookies, get_jwt_identity

app = Flask(__name__)
app.secret_key = "01d2acfd81084d598c66178ce738dbf3"
db_api = BillDBAPI()

# Here you can globally configure all the ways you want to allow JWTs to
# be sent to your web application. By default, this will be only headers.
app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies", "json", "query_string"]

# If true this will only allow the cookies that contain your JWTs to be sent
# over https. In production, this should always be set to True
app.config["JWT_COOKIE_SECURE"] = False

# Set the secret key to sign the JWTs with
app.config['JWT_SECRET_KEY'] = 'iuashd981ehiuhqew9112897'  # Change this from 'secret'


jwt = JWTManager(app)
# Load templates
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
@jwt_required()
def dashboard():
    return render_template('dashboard.html')


@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

todays_date = date.today()


# Create bill
@app.post("/api/user")
def create_user():
    
    # get json data
    json_data = request.get_json()

    # check if signup username exists in database
    users = db_api.get_all_users()
    
    for user in users:
        if user.username == json_data["username"]:
            return {"msg":f"Username already exists in database."}, 400
        elif user.email == json_data["email"]:
            return {"msg":f"Email already exists in database."}, 400
    # check if password matches repeated password check
    if json_data["password"] != json_data["repeatPassword"]:
        return {"msg":"Passwords do not match"}, 400
    
    # delete repeat password from payload
    del json_data["repeatPassword"]

    # deserialize json to UserCreate object with no ID (not created yet in DB)
    new_user = deserialize_json(UserCreate, json_data)
    db_api.create_user(new_user)
    
    # return user just created by getting it from database by username
    # then deserializing to object, then turn into json
    return {"msg":"signup successful"}, 200

@app.get("/api/user")
def get_users():
    users = db_api.get_all_users()

    deserialized_users= serialize_to_json(users)
    return deserialized_users, 200

@app.delete("/api/user")
def delete_all_users():
    pass


@app.route("/login_with_cookies", methods=["POST"])
def login_with_cookies():
    response = jsonify({"msg": "login successful"})
    data = request.get_json()

    if authenticate_user(data):
        user = db_api.get_user_by_username(data["username"])
        access_token = create_access_token(identity=user.id)
        
        set_access_cookies(response, access_token)
        
        return response
    return {"msg":"login failed"}

@app.route("/logout_with_cookies", methods=["POST"])
def logout_with_cookies():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response


@app.route("/protected", methods=["GET", "POST"])
@jwt_required()
def protected():

    return jsonify(foo="bar", id=get_jwt_identity())



# Create bill
@app.route("/bill", methods=["POST"])
#@app.post("/bill")
@jwt_required()
def create_bill():
    
    # get json data
    json_data = request.get_json()

    # deserialize json to Bill object with no ID or user ID (not created yet in DB)
    new_bill = deserialize_json(BillCreate, json_data)
    
    # get user by id

    user = db_api.get_user_by_id(get_jwt_identity())

    #TODO add user_id value to bill here
    new_bill.user_id = user.id
    
    #validates that data meets certain specifications
    if validate(new_bill, todays_date) != None:
        
        return validate(new_bill, todays_date), 404
    
    # Return created bill from DB to verify completion
    return serialize_to_json(db_api.create_bill(new_bill, get_jwt_identity())), 200


# Get all bills
@app.get("/bill")
@jwt_required()
def get_all_bills():
    
    # TODO replace with API all_bills = database.show_all()

    sorted_bills = sort_bills_by_date(db_api.get_all_bills(get_jwt_identity()))
    
    deserialized_bills = serialize_to_json(sorted_bills)

    return deserialized_bills, 200


# Get specific bill ID
@app.get("/bill/<string:id>")
@jwt_required()
def get_bill_by_id(id: str):
    bill = deserialize_row(Bill, db_api.get_bill_by_id(id), todays_date)

    return serialize_to_json(bill), 201


# Delete specific bill by ID
@jwt_required()
@app.delete("/bill/<string:id>")
def delete_bill_by_id(id):

    return db_api.delete_bill_by_id(id)



@app.put("/bill/<string:id>")
@jwt_required()
def update_bill(id):

    # TODO edit bill
    jdata = request.get_json()

    # get specific bill from db
    bill = deserialize_row(Bill, db_api.get_bill_by_id(id), todays_date)

    
    # edit replace bill with new jdata
    edited_bill = edit_bill(bill, jdata)
    
    validated = validate(edited_bill, todays_date)
    if  validated != None:
        return validated, 404
    
    # update the bill and return the new bill from DB
    return serialize_to_json(db_api.update_bill(id, edited_bill))


def authenticate_user(data: dict) -> bool:
    '''Return true of false on whether or not user creds are valid
    Gets user creds from db and compares to log in creds fetched from front end
    '''

    uname = data['username'] 
    pword = data['password']

    user = db_api.get_user_by_username(uname)
    
    if isinstance(user,Exception):

        return False
    else:

        return check_password_hash(user.password, pword)

