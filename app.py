from flask import Flask, request
import database
import sqlite3
import uuid
import decimal  # use this instead
from Deserializer import deserialize_row, deserialize_rows, Bill
from orjson import dumps, loads

from datetime import date

app = Flask(__name__)

# Keys for bills serializer
keys = ["bill_id", "bill_name", "amount", "due_date"]
def foo(x: int) -> int:
    return "yes"


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
    bill_name: str = json_data['name']
    bill_amount: decimal = decimal.Decimal(json_data['amount'])
    due_date: int = int(json_data['due_date'])

    # create due date object
    current_date = date.today()

    # check if due date has passed or not
    try:
        if current_date.day <= int(due_date):  # Due this month

            # create due date object with due date being this month
            due_date_obj: date = date(current_date.year, current_date.month, int(due_date))
            date_difference = due_date_obj - current_date

        elif current_date.day  > int(due_date):  # Due next month (add month to date object)

            # add month to current month
            if current_date.month == 12:  # if current month is 12, set to january
                due_date_obj = date(current_date.year, 1, int(due_date))
            else:  # current month is less than 12
                due_date_obj = date(current_date.year, current_date.month + 1, int(due_date))

            # get difference in days before next bill is due
            date_difference = due_date_obj - current_date


    except ValueError:
        return {"message": "Date you entered for month was not valid."}, 404

    # add bill to DB
    database.create_bill_record(bill_name, bill_amount, due_date_obj)

    return {"message": "Everything went well"}, 200

# Get all bills
@app.get("/bill")
def get_all_bills():
    all_bills = database.show_all()

    deser = deserialize_rows(Bill, all_bills)
    #print(deser)
    return deser, 200

# Get specific bill ID
@app.get("/bill/<string:id>")
def get_bill(id):
    bill = database.select_record_by_id(id)

    deser = deserialize_row(Bill, bill[0])

    return deser, 201

# Delete specific bill by ID
@app.delete("/bill/<string:id>")
def delete_bill_by_id(id):
    database.delete_record_by_id(id)
    return {"message": "Record has been deleted"}, 200

    # sort list by days left
