from flask import Flask, request
from flask_smorest import Api
from db import bills
import uuid

from datetime import datetime,date
from dateutil.relativedelta import relativedelta


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

    
    # create due date object
    current_date = date.today()
    due_date = json_data['due_date']

    # check if due date has passed or not
    if current_date.day < int(due_date): # Due this month

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
        # dateutil was not working for some reason when i wanted to subtract days
    
    # create new UUID
    id = uuid.uuid4().hex
    new_bill = {**json_data, "bill_id":id, "due_date":due_date, "days_left":date_difference.days }
    
    # add bill to DB
    bills[id] = new_bill
    print(bills)
    return new_bill

@app.get("/bill")
def get_all_bills():
    
    return list(bills.values())

@app.get("/bill/<string:id>")
def get_bill(id):
    if id not in bills:
        return {"message":"ID not valid, no bill with entered ID."}, 404
    else:
        return bills[id]