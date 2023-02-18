import sqlite3
from _decimal import Decimal
from datetime import date
from data_handler import *
from BillAPI import BillAPI
from data_handler import Bill, BillCreate, User, UserCreate
from uuid import uuid4
from werkzeug.security import generate_password_hash, check_password_hash

todays_date = date.today()
class BillDBAPI(BillAPI):

    def create_user(self, UserCreate):
        #connects to db we name,if it doesn't exist will create it
        conn = sqlite3.connect("bill.db")

        # create cursor
        c = conn.cursor()

        # generate UUID
        id = uuid4().hex
        
        # hash password
        hashed_pass =  generate_password_hash(UserCreate.password,method="sha256")
        c.execute("INSERT INTO Users VALUES (?,?,?,?)", (id, 
        UserCreate.username,
        hashed_pass,
        UserCreate.email))

        conn.commit()
        conn.close()
    def get_all_users(self) -> list[User]:
        # connects to db we name,if table doesn't exist will create it
        conn = sqlite3.connect("bill.db")

        # create cursor
        c = conn.cursor()

        # Query the whole DB
        c.execute("SELECT * FROM Users")
        fetched = c.fetchall()

        # Commit our command
        conn.commit()

        # Close our connection
        conn.close()
        print("before deserialized", fetched)
        deserialized_users= deserialize_rows(User, fetched)
        print("DESERIALIZED USERS ", deserialized_users)
        return deserialized_users

    def create_bill(self, new_bill: BillCreate) -> Bill:
        """Takes BillCreate (Bill without ID), and adds to database 
        and returns the Bill object with the ID
        """
        # connects to db we name,if it doesn't exist will create it
        conn = sqlite3.connect("bill.db")

        # create cursor
        c = conn.cursor()

        # generate UUID
        id = uuid4().hex
        
        c.execute("INSERT INTO bills VALUES (?,?,?,?)", (id, new_bill.name,
                                                            dollars_to_cents(new_bill.amount),
                                                            new_bill.due_date))

        conn.commit()
        conn.close()

        # return bill not that its been created in DB so it can be returned to user

        # returns created bill
        return deserialize_row(Bill, self.get_bill_by_id(id),todays_date)

    # Query the DB return all records
    def get_all_bills(self) -> list[Bill]:
        # connects to db we name,if table doesn't exist will create it
        conn = sqlite3.connect("bill.db")

        # create cursor
        c = conn.cursor()

        # Query the whole DB
        c.execute("SELECT * FROM bills")
        fetched = c.fetchall()

        # Commit our command
        conn.commit()

        # Close our connection
        conn.close()
        print("inside db get all funciton, before deserialization", fetched)
        deserialized_bills = deserialize_rows(Bill, fetched)
        return deserialized_bills

    def get_bill_by_id(self, id: str) -> list[tuple[object]]:
        # connects to db we name,if table doesn't exist will create it
        conn = sqlite3.connect("bill.db")

        # create cursor
        c = conn.cursor()

        c.execute("SELECT * FROM bills WHERE id = ? ", [id])
        bill_row = c.fetchall()

        conn.commit()
        conn.close()

        return bill_row

    def delete_bill_by_id(self, id: str) -> dict:
        """ Deletes bill from database"""
        conn = sqlite3.connect("bill.db")

        # create cursor
        c = conn.cursor()

        c.execute("DELETE FROM bills WHERE id = ? ", [id])

        conn.commit()
        conn.close()
        return {"message": "Bill has been deleted"}

    # TODO implement edit bill
    def update_bill(self, id: str, edited_bill: Bill) -> Bill:
        conn = sqlite3.connect("bill.db")

        # create cursor
        c = conn.cursor()

        c.execute("UPDATE bills SET name=?, amount=?, due_date=? WHERE id = ? ",
                    [edited_bill.name, dollars_to_cents(edited_bill.amount), edited_bill.due_date, edited_bill.id])

        conn.commit()
        conn.close()
        return deserialize_row(Bill, self.get_bill_by_id(id), todays_date)


# Other functions
def get_largest_rowid() -> int:
    # connects to db we name,if it doesn't exist will create it
    conn = sqlite3.connect("bill.db")

    # create cursor
    c = conn.cursor()

    c.execute("SELECT * FROM bills ORDER BY id DESC LIMIT 1;")
    result: list[tuple[int]] = c.fetchall()
    conn.commit()
    conn.close()
    if result == []:
        return 0
    else:
        return result[0][0]


def _auto_increment_db() -> int:
    incremented = get_largest_rowid() + 1
    return incremented


# connects to db we name,if table doesn't exist will create it
conn = sqlite3.connect("bill.db")

# create cursor
c = conn.cursor()
data = c.execute('''
-- CREATE TABLE users (
-- 	user_id TEXT PRIMARY KEY,
-- 	username TEXT NOT NULL UNIQUE,
-- 	password TEXT NOT NULL,
-- 	email TEXT NOT NULL UNIQUE
-- )
''')

conn.commit()
conn.close()
