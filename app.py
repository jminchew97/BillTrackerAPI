from flask import Flask, request
import database
import sqlite3
import uuid
import decimal  # use this instead
from data_handler import *
from orjson import dumps, loads

from datetime import date

app = Flask(__name__)


# Keys for bills serializer

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
    # get json data
    json_data = request.get_json()


    # deserialize json
    new_bill = deserialize_json_on_post(Bill, json_data)
    #TODO: get date difference of due_date_obj and current_date for "days_left"

    # add bill to DB, convert bill amount to float for storage only
    database.create_bill_record(new_bill)

    return serialize_to_json(new_bill), 200


# Get all bills
@app.get("/bill")
def get_all_bills():
    all_bills = database.show_all()

    deserialized_bills = deserialize_rows(Bill, all_bills)

    # print(deser)
    return deserialized_bills, 200


# Get specific bill ID
@app.get("/bill/<string:id>")
def get_bill(id):
    bill_sqlite = database.select_record_by_id(id)

    bill_obj = deserialize_row(Bill, bill_sqlite[0])

    return serialize_to_json(bill_obj), 201


# Delete specific bill by ID
@app.delete("/bill/<string:id>")
def delete_bill_by_id(id):
    database.delete_record_by_id(id)
    return {"message": "Record has been deleted"}, 200

    # sort list by days left


@app.put("/bill/<string:id>")
def edit_bill(id):

    # get json_data
    json_data = request.get_json()

    # add id to json data
    json_data["id"] = int(id)

    # get bill data based on id number, deserialize data to Bill obj

    bill = deserialize_row(Bill, database.select_record_by_id(id))

    # for field in fields(bill):
    #     print(field)
    return {"1":1}
    # validate json data


    #assign new values


