import sqlite3
from _decimal import Decimal
from datetime import date
from data_handler import dollars_to_cents, Bill


# Query the DB return all records
def show_all() -> list[tuple[object]]:
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
    return fetched


def create_bill_record(new_bill: Bill) -> None:
    # connects to db we name,if it doesn't exist will create it
    conn = sqlite3.connect("bill.db")

    # create cursor
    c = conn.cursor()
    c.execute("INSERT INTO bills VALUES (?,?,?,?)", (auto_increment_db(), new_bill.name,
                                                     dollars_to_cents(new_bill.amount),
                                                     new_bill.due_date))
    conn.commit()
    conn.close()


def select_record_by_id(id: int) -> list[tuple[object]]:
    # connects to db we name,if table doesn't exist will create it
    conn = sqlite3.connect("bill.db")

    # create cursor
    c = conn.cursor()

    c.execute("SELECT * FROM bills WHERE id = ? ", id)
    bill_row = c.fetchall()

    conn.commit()
    conn.close()

    return bill_row


def delete_record_by_id(id: int) -> None:
    # connects to db we name,if doesnt exist will create it
    conn = sqlite3.connect("bill.db")

    # create cursor
    c = conn.cursor()

    c.execute("DELETE FROM bills WHERE id = ? ", id)

    conn.commit()
    conn.close()


# TODO: finish function (needs json deserializer)
# def edit_user(id: int) -> None:
#     # connects to db we name,if doesnt exist will create it
#     conn = sqlite3.connect("bill.db")
#
#     # create cursor
#     c = conn.cursor()
#
#     # TODO: needs a json deserializer so i can access the fields and finish this SQLITE command
#     c.execute("""UPDATE bills SET BILL_NAME = 'Electric' WHERE rowid=?""", str(id)) # must use single quotes for value if text
#
#     conn.commit()
#     conn.close() ## TODO: #

def get_largest_rowid() -> int:
    # connects to db we name,if it doesn't exist will create it
    conn = sqlite3.connect("bill.db")

    # create cursor
    c = conn.cursor()

    c.execute("SELECT * FROM bills ORDER BY id DESC LIMIT 1;")
    result: list[tuple[int]] = c.fetchall()

    if result == []:
        return 0
    else:
        return result[0][0]
    conn.commit()
    conn.close()


def auto_increment_db() -> int:
    incremented = get_largest_rowid() + 1
    return incremented


# connects to db we name,if table doesn't exist will create it
conn = sqlite3.connect("bill.db")

# create cursor
c = conn.cursor()

conn.commit()
conn.close()
