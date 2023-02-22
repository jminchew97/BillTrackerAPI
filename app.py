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
from flask_jwt_extended import unset_jwt_cookies

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
    authenticate_user(json)
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

    # deserialize json to UserCreate object with no ID (not created yet in DB)
    new_user = deserialize_json(UserCreate, json_data)
    db_api.create_user(new_user)
    
    # return user just created by getting it from database by username
    # then deserializing to object, then turn into json
    return serialize_to_json(deserialize_row(User, db_api.get_user_by_username(new_user.username))), 200

@app.get("/api/user")
def get_users():
    users = db_api.get_all_users()
    print(f"all users   {users}")
    deserialized_users= serialize_to_json(users)
    return deserialized_users, 200

@app.delete("/api/user")
def delete_all_users():
    pass


@app.route("/login_with_cookies", methods=["POST"])
def login_with_cookies():
    response = jsonify({"msg": "login successful"})
    if authenticate_user(request.get_json()):

        access_token = create_access_token(identity="example_user")
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
    return jsonify(foo="bar")



# Create bill
@app.post("/bill")
def create_bill():
    # get json data
    json_data = request.get_json()

    # deserialize json to Bill object with no ID (not created yet in DB)
    new_bill = deserialize_json(BillCreate, json_data)
    
    print(f"current date test: {todays_date}")
    #validates that data meets certain specifications
    if validate(new_bill, todays_date) != None:
        
        return validate(new_bill, todays_date), 404
    
    # Return created bill from DB to verify completion
    return serialize_to_json(db_api.create_bill(new_bill)), 200


# Get all bills
@app.get("/bill")
def get_all_bills():
    # TODO replace with API all_bills = database.show_all()

    sorted_bills = sort_bills_by_date(db_api.get_all_bills())

    deserialized_bills = serialize_to_json(sorted_bills)

    return deserialized_bills, 200


# Get specific bill ID
@app.get("/bill/<string:id>")
def get_bill_by_id(id: str):
    bill = deserialize_row(Bill, db_api.get_bill_by_id(id), todays_date)

    return serialize_to_json(bill), 201


# Delete specific bill by ID
@app.delete("/bill/<string:id>")
def delete_bill_by_id(id):

    return db_api.delete_bill_by_id(id)


# TODO create edit bill function
@app.put("/bill/<string:id>")
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
    '''Return true of false on whether or not user creds are valid'''
    print(data)
    uname = data['username'] 
    pword = data['password']

    user = db_api.get_user_by_username(uname)
    
    if isinstance(user,Exception):
        print("login failed in auth function")
        return False
    else:
        print("login passed in auth function")
        return check_password_hash(user.password, pword)
