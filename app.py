from flask import Flask, request
from flask_smorest import Api
import database
import sqlite3
import uuid

from datetime import date


app = Flask(__name__)

@app.post("/bill")
def create_bill():

    """Create a new bill\n
    
    Expected JSON data:\n
    STR"name"-name of bill\n
    FLOAT"amount"-bill amount\n
    STR"due_date"-due date\n
    BOOL"fixed_amount"-is the amount the same every month or does it change
    
    
    """
    json_data = request.get_json()
    bill_name = json_data['name']
    bill_amount = json_data['amount']
    due_date = json_data['due_date']
    
    # create due date object
    current_date = date.today()

    # check if due date has passed or not
    try:
        if current_date.day < int(due_date): # Due this month

            # create due date object with due date being this month
            due_date = date(current_date.year, current_date.month, int(due_date))
            date_difference = due_date - current_date

        elif current_date.day > int(due_date): # Due next month (add month to date object)
            
            # add month to current month
            if current_date.month == 12: # if current month is 12, set to january
                due_date = date(current_date.year, 1, int(due_date))
            else: # month is less than 12
                due_date = date(current_date.year, current_date.month+1, int(due_date))
            
            # get difference in days before next bill is due
            date_difference = due_date-current_date
    except ValueError:
        return {"message":"Date you enters for month was not valid."}, 404
 
    # add bill to DB
    database.create_bill_record(bill_name, bill_amount, due_date)
    
    return {"message":"Everything went well"}, 200


@app.get("/bill")
def get_all_bills():
    all_items = database.show_all()
    return all_items, 200

@app.get("/bill/<string:id>")
def get_bill(id):
    return database.select_record_by_id(id), 200

@app.delete("/bill/<string:id>")
def delete_bill_by_id(id):
    database.delete_record_by_id(id)
    return {"message":"Record has been deleted"}, 200


print("Hello")