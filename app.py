from flask import Flask, request, render_template, flash

from database_api import BillDBAPI
from data_handler import *

from datetime import date

app = Flask(__name__)
db_api = BillDBAPI()


# Load templates
@app.route('/')
def index():
    flash("this is a flash test")
    return render_template('index.html')


@app.route('/dashboard')
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
    return {"m":"everything good"}

@app.get("/api/user")
def get_users():
    users = db_api.get_all_users()
    print(f"all users   {users}")
    deserialized_users= serialize_to_json(users)
    return deserialized_users, 200

# Create bill
@app.post("/bill")
def create_bill():
    # get json data
    json_data = request.get_json()

    # deserialize json to Bill object with no ID (not created yet in DB)
    new_bill = deserialize_json(BillCreate, json_data)
    
    print(f"current date test: {todays_date}")
    #validation 
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
