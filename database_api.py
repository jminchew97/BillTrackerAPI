import sqlite3
from _decimal import Decimal
from datetime import date
from data_handler import *
from BillAPI import BillAPI
from data_handler import Bill, BillCreate
from uuid import uuid4


class BillDBAPI(BillAPI):
    def create_bill(self, new_bill: BillCreate) -> Bill:
        # connects to db we name,if it doesn't exist will create it
        conn = sqlite3.connect("bill.db")

        # create cursor
        c = conn.cursor()

        # adding in id at time of record creation
        id = _auto_increment_db()
        c.execute("INSERT INTO bills VALUES (?,?,?,?)", (id, new_bill.name,
                                                         dollars_to_cents(new_bill.amount),
                                                         new_bill.due_date))

        conn.commit()
        conn.close()

        # return bill not that its been created in DB so it can be returned to user

        # returns created bill
        return deserialize_row(Bill, self.get_bill_by_id(str(id)))

    # Query the DB return all records
    def get_all_bills(self) -> list[object]:
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

        deserialized_bills = deserialize_rows(Bill, fetched)
        return deserialized_bills

    def get_bill_by_id(self, id: str) -> list[tuple[object]]:
        # connects to db we name,if table doesn't exist will create it
        conn = sqlite3.connect("bill.db")

        # create cursor
        c = conn.cursor()

        c.execute("SELECT * FROM bills WHERE id = ? ", id)
        bill_row = c.fetchall()

        conn.commit()
        conn.close()

        return bill_row

    def delete_bill_by_id(self, id: str) -> dict:
        """ Deletes bill from database"""
        conn = sqlite3.connect("bill.db")

        # create cursor
        c = conn.cursor()

        c.execute("DELETE FROM bills WHERE id = ? ", id)

        conn.commit()
        conn.close()
        return {"message": "Bill has been deleted"}

    # TODO implement edit bill
    def edit_bill_by_id(self, id: str) -> Bill:

        pass

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

conn.commit()
conn.close()
