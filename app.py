from flask import Flask, request

from database_api import BillDBAPI
from data_handler import *

from datetime import date

app = Flask(__name__)
db_api = BillDBAPI()


# Keys for bills serializer


@app.post("/bill")
def create_bill():
    # get json data
    json_data = request.get_json()

    # deserialize json to Bill object with no ID (not created yet in DB)
    new_bill = deserialize_json(BillCreate, json_data)

    # TODO add get_bill_by_ID
    return serialize_to_json(db_api.create_bill(new_bill)), 200


# Get all bills
@app.get("/bill")
def get_all_bills():
    # TODO replace with API all_bills = database.show_all()

    deserialized_bills = serialize_to_json(db_api.get_all_bills())

    # print(deser)
    return deserialized_bills, 200


# Get specific bill ID
@app.get("/bill/<string:id>")
def get_bill_by_id(id: str):
    bill = deserialize_row(Bill, db_api.get_bill_by_id(id))

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
    bill = deserialize_row(Bill, db_api.get_bill_by_id(id))

    # edit replace bill with new jdata
    edited_bill = edit_bill(bill, jdata)

    # update the bill and return the new bill from D
    return serialize_to_json(db_api.update_bill(id, edited_bill))
