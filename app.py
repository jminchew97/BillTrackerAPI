from flask import Flask, request, render_template, redirect, url_for
from werkzeug.security import check_password_hash
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from database_api import BillDBAPI
from data_handler import *
import uuid
from datetime import date

app = Flask(__name__)
app.secret_key = uuid.uuid4().hex
db_api = BillDBAPI()

app.config['JWT_ACCESS_COOKIE_PATH'] = '/api/'
app.config['JWT_REFRESH_COOKIE_PATH'] = '/token/refresh'

# Disable CSRF protection for this example. In almost every case,
# this is a bad idea. See examples/csrf_protection_with_cookies.py
# for how safely store JWTs in cookies
app.config['JWT_COOKIE_CSRF_PROTECT'] = False

# Set the secret key to sign the JWTs with
app.config['JWT_SECRET_KEY'] = 'iuashd981ehiuhqew9112897'  # Change this!

# Load templates
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
@login_required
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

@app.post("/api/login")
def login_user():
    if current_user.is_authenticated:
        print("user is authenticated")
        return redirect(url_for("dashboard"))
    
    # user not authenticated, check login info
    jdata = request.get_json()
    #user = db_api.get_user_by_username(jdata['username'])
    user = load_user(jdata["username"])
    user_password = user[0][2]
    entered_password = jdata['password']
    
    if check_password_hash(user_password, entered_password):
        login_user(user)
    return {"aye":str(check_password_hash(user_password, jdata['password']))}
    

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
