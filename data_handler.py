import dataclasses
from typing import TypeVar, Optional
from dataclasses import dataclass, fields, replace
from dataclasses_json import dataclass_json
from decimal import Decimal
from uuid import uuid4
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import orjson
import json as json_module

import data_handler


def cents_to_dollars(cents_amount: int) -> Decimal:
    dollars = round(Decimal(cents_amount / 100), 2)
    return Decimal(dollars)


@dataclass_json
@dataclass
class Bill:
    """A finished bill object including all fields, has been already committed to database"""
    id: str
    name: str
    amount: Decimal
    due_date: date


@dataclass_json
@dataclass
class BillCreate:
    name: str
    amount: Decimal
    due_date: date


@dataclass_json
@dataclass
class BillEdit:
    name: Optional[str] = None
    amount: Optional[Decimal] = None
    due_date: Optional[date] = None


T = TypeVar('T')


# test

# default class for orjson, will auto convert objects not used by orjson
def default(obj: type[T]):
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError


#                 (Type of object) (list)
def deserialize_row(typ: type[T], row: list[tuple[object]]) -> T:
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
            deserialized_values.append(datetime.strptime(value, "%Y-%m-%d").date())

        # converts to decimal while also converting from_cents_to_dollars, only if this is an "amount" of money
        elif field_type == Decimal and field.name == "amount":
            deserialized_values.append(cents_to_dollars(value))

        elif field_type == Decimal:  # not an amount of money
            deserialized_values.append(Decimal(value))

    # create new type, unpack dezerialized_values
    new_typ = typ(*deserialized_values)

    return new_typ


def deserialize_rows(typ: type[T], rows: list[tuple[object]]) -> list[T]:
    return [deserialize_row(typ, row) for row in rows]


def serialize_to_json(typ: dataclasses.dataclass()) -> dict:
    json_byte: bytes = orjson.dumps(typ, default=default)
    json = orjson.loads(json_byte)
    return json  # returns dict


def deserialize_json(typ: type[T], jdata: dict) -> T:
    # convert due_date ex. 15, to date obj and add to payload
    jdata = add_date_obj_to_payload(jdata)

    # deserialize json payload
    new_typ = typ.from_json(orjson.dumps(jdata))
    return new_typ


def edit_bill(bill_obj: Bill, jdata: dict) -> Bill:
    jdata = add_date_obj_to_payload(jdata)

    # check if update bill in jdata

    edited_bill = replace(bill_obj, **jdata)

    return edited_bill


def add_date_obj_to_payload(jdata: dict) -> dict:
    if "due_date" in jdata:
        jdata["due_date"] = str_to_date_obj(jdata["due_date"])
    return jdata


def dollars_to_cents(dollar_amount: Decimal) -> int:
    if not isinstance(dollar_amount, Decimal):
        dollar_amount = Decimal(dollar_amount)

    cents = int(dollar_amount * 100)
    return cents


def str_to_date_obj(due_date: int) -> date:
    due_date = int(due_date)
    current_date = date.today()
    try:
        if current_date.day <= due_date:  # Bill due this month

            # create due date object with due date being this month
            due_date_obj: date = date(current_date.year, current_date.month, due_date)
            date_difference = due_date_obj - current_date

        elif current_date.day > due_date:  # Bill due next month (add month to date object)
            return increment_month(due_date)

    except ValueError:
        return {"message": "Date you entered for month was not valid."}, 404


def check_if_due_date_passed(bill: Bill) -> Bill:
    current_date = date.today()
    # if bill.due_date < current_date:
    bill.due_date = increment_month(bill.due_date.day)

    return bill


def increment_month(due_date: int) -> date:
    """return date object with due_date being NEXT month"""
    due_date_obj = date(date.today().year, date.today().month, due_date)

    due_date_obj = due_date_obj + relativedelta(months=1)
    return due_date_obj


# tests

new_bill = Bill("123", "Electric", Decimal(12), date(2023, 12, 29))

date1 = date(2022,1,25)
date2 = date(2022,12,25)