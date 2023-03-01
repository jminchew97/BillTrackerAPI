
from typing import TypeVar, Optional
from dataclasses import dataclass, fields, replace
from dataclasses_json import dataclass_json
from decimal import Decimal
from uuid import uuid4
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import orjson, re, dataclasses
import json as json_module


@dataclass_json
@dataclass
class UserCreate:
    """user without id, going into db"""
    username: str
    password: str
    email:str
@dataclass_json
@dataclass
class User:
    """A finished user object including all fields, extracting from db"""
    id: str
    """Hashed password as str"""
    username: str
    password: str
    email:str
@dataclass_json
@dataclass
class Bill:
    """A finished bill object including all fields, has been already committed to database"""
    id: str
    name: str
    amount: Decimal
    due_date: date
    user_id:str

@dataclass_json
@dataclass
class BillCreate:
    name: str
    amount: Decimal
    due_date:date

@dataclass_json
@dataclass
class BillEdit:
    name: Optional[str] = None
    amount: Optional[Decimal] = None
    due_date: Optional[date] = None
    user_id: Optional[str] = None # TODO must find a way to make sure user_id is required

T = TypeVar('T')


# test

# default class for orjson, will auto convert objects not used by orjson
def default(obj: type[T]):
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError



def deserialize_row(typ: type[T], row: list[tuple[object]], current_date: date = date.today()) -> T:
    """deserialize row from SQLITE"""

    # checks to see if there's single row in the returned list i.e [[1,"a",12.3]],
    # rather than [[1,"a",12.3], [1,"a",12.3]]
    if len(row) == 1:  # if so, selects that row to iterate through
        row = row[0]

    # List to hold values after casted to proper type
    deserialized_values = []

    # make sure values are equal to expected fields
    if len(fields(typ)) != len(row):
        return Exception(f"{len(fields(typ))} fields were expected, recieved {len(row)}")

    # iterate through typ field with corresponding value
    for field, value in zip(fields(typ), row):

        field_type = typ.__annotations__[field.name]
        # check what type current field is expecting, then cast value given to that type
        # then append to deserialized_values
        if field_type == int:
            deserialized_values.append(value)

        elif field_type == str:
            deserialized_values.append(str(value))

        elif field_type == date:
            try:

                due_date = set_due_date(datetime.strptime(value, "%Y-%m-%d").date(), current_date )
            except:
                print("Missing current_date argument")
            deserialized_values.append(due_date)

            
        # converts to decimal while also converting from_cents_to_dollars, only if this is an "amount" of money
        elif field_type == Decimal and field.name == "amount":
            deserialized_values.append(cents_to_dollars(value))

        elif field_type == Decimal:  # not an amount of money
            deserialized_values.append(Decimal(value))

    # create new type, unpack dezerialized_values
    new_typ = typ(*deserialized_values)

    
    return new_typ


def deserialize_rows(typ: type[T], rows: list[tuple[object]]) -> list[T]:
    return [deserialize_row(typ, row ) for row in rows]


def serialize_to_json(typ: type[T]) -> dict:
    json_byte: bytes = orjson.dumps(typ, default=default)
    json = orjson.loads(json_byte)
    return json  # returns dict

def cents_to_dollars(cents_amount: int) -> Decimal:
    dollars = round(Decimal(cents_amount / 100), 2)
    return Decimal(dollars)
def validate(typ: type[T], current_date: date) :
    """validates type (BillCreate, Bill, EditBill
    makes sure that amount is greater than 0, can add more validation later if needed on name, date, etc
    """
    
    # iterate through typ field with corresponding value
    print(typ, "<=====================")
    for field in fields(typ):
        
        # converts to decimal while also converting from_cents_to_dollars, only if this is an "amount" of money
        if getattr(typ, field.name) != None:
            
            if field.name == "amount":
                amount = getattr(typ, field.name)
                
                for char in amount:

                    # char is not a period and is not a digit, must be invalid character
                    if char != "." and str.isdigit(char) == False:
                        print("cahr error in amount", amount)
                        return {"message":f"Entered invalid character '{char}'"}
                    
                if amount == "" or getattr(typ, field.name) == None:
                    return {"message":"You must enter a valid amount. Only numbers or a decimal. ex => 123384.28, 1235343"}
                
                if Decimal(amount) <= 0:
                    return {"message":"Number must be greater than 0"}
                
            elif field.name == "due_date":
                date= getattr(typ, field.name)

                if isinstance(date, str):
                    date = str_to_date_obj(date, current_date)
                
                if date.day > 28:
                    return {"message":"You must have a reccuring date below 29th"}
    return None

def deserialize_json(typ: type[T], jdata: dict, current_date:date = date.today()) -> T:
    if "due_date" in jdata:
        jdata["due_date"] = str_to_date_obj(jdata["due_date"], current_date)

    # deserialize json payload
    new_typ = typ(**jdata)
    
    return new_typ


def edit_bill(bill_obj: Bill, jdata: dict) -> Bill:

    # check if update bill in jdata

    edited_bill = replace(bill_obj, **jdata)

    return edited_bill





def dollars_to_cents(dollar_amount: Decimal) -> int:
    if not isinstance(dollar_amount, Decimal):
        dollar_amount = Decimal(dollar_amount)

    cents = int(dollar_amount * 100)
    return cents


def str_to_date_obj(due_date_str: str, current_date: date) -> date:


    # create date from formated date string from client
    user_due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
    
    return set_due_date(user_due_date, current_date)


def set_due_date(user_due_date: date, current_date:date) -> date:
    # make due date this month so we can calculate when its NEXT due
    due_date = date(current_date.year, current_date.month, user_due_date.day)
    try:
        if current_date.day > due_date.day:  # Bill due next month (add month to date object)

            return increment_month(due_date)
        else:
            return due_date
    except ValueError:
        return {"message": "Date you entered for month was not valid."}, 404


def update_due_date(bill: Bill, current_date: date) -> Bill:

    # set updated due date to current month and year
    updated_due_date = date(current_date.year, current_date.month, bill.due_date.day)

    if bill.due_date < current_date:

        # if due_day is less than current day, increment month
        if bill.due_date.day < current_date.day:
            updated_due_date = increment_month(updated_due_date)

    bill.due_date = updated_due_date

    return bill


def increment_month(due_date: date) -> date:
    """return date object with due_date being NEXT month"""

    due_date_obj = due_date + relativedelta(months=1)
    return due_date_obj

def sort_bills_by_date(bills: list[Bill] ) -> list[Bill]:
    bills.sort(key=lambda x: x.due_date)

    return bills


