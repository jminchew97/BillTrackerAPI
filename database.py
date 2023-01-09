import sqlite3



# Query the DB return all records
def show_all():
    # connects to db we name,if doesnt exist will create it
    conn = sqlite3.connect("bill.db")

    # create cursor
    c = conn.cursor()

    # Query the whole DB
    c.execute("SELECT rowid, * FROM bills")
    fetched = c.fetchall()

    # Commit our command
    conn.commit() 

    # Close our connection
    conn.close()
    return fetched

def create_bill_record(bill_name, amount, due_date):
    # connects to db we name,if doesnt exist will create it
    conn = sqlite3.connect("bill.db")

    # create cursor
    c = conn.cursor()

    c.execute("INSERT INTO bills VALUES (?,?,?)", (bill_name, amount, due_date))
    conn.commit()
    conn.close()

def select_record_by_id(id):
    # connects to db we name,if doesnt exist will create it
    conn = sqlite3.connect("bill.db")

    # create cursor
    c = conn.cursor()

    c.execute("SELECT * FROM bills WHERE rowid = ? ", id)
    bill = c.fetchall()

    conn.commit()
    conn.close()

    return bill
def delete_record_by_id(id):
    # connects to db we name,if doesnt exist will create it
    conn = sqlite3.connect("bill.db")

    # create cursor
    c = conn.cursor()

    c.execute("DELETE FROM bills WHERE rowid = ? ", id)
    
    conn.commit()
    conn.close()

#DATATYPES:
#null
#integer
#real
#text
#blob

