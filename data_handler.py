import dataclasses
from typing import TypeVar, Optional
from dataclasses import dataclass, fields, replace
from dataclasses_json import dataclass_json
from decimal import Decimal
from datetime import date, datetime
import orjson
import json as json_module

import data_handler
def cents_to_dollars(cents_amount: int) -> Decimal:
    dollars = round(Decimal(cents_amount / 100), 2)
    print(f"{cents_amount} -> {dollars}")
    return Decimal(dollars)

@dataclass_json
@dataclass
class Bill:
    """A finished bill object including all fields, has been already committed to database"""
    id: int
    name: str
    amount: Decimal
    due_date: datetime.date


@dataclass_json
@dataclass
class BillCreate:
    """A bill data type with no id because it has not been generated and stored in the database yet"""
    name: str
    amount: Decimal
    due_date: datetime.date


@dataclass_json
@dataclass
class BillEdit:
    id: int
    name: Optional[str] = None
    amount: Optional[Decimal] = None
    due_date: Optional[datetime.date] = None


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
        # check what type current field is expecting, then cast corresponding value to that type
        # then append to deserialized_values
        if field_type == int:
            deserialized_values.append(int(value))

        elif field_type == str:
            deserialized_values.append(str(value))

        elif field_type == datetime.date:
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


def deserialize_json_on_post(typ: type[T], json_data: dict) -> T:
    if typ == BillCreate:
        print(f"Type of argument before error : {type(round(Decimal(json_data['amount']), 2))}")
        new_bill = BillCreate(json_data["name"], round(Decimal(json_data['amount']), 2),
                              str_to_date_obj(json_data["due_date"]))

    else:
        raise Exception("Dont know how to deserialize this type of object. You entered type {type(typ}.")
    return new_bill


def deserialize_json_on_put(typ: type[T], jdata: dict) -> T:
    new_bill = BillEdit(1)

    edited_bill = replace(new_bill, **jdata)

    return edited_bill


def dollars_to_cents(dollar_amount: Decimal) -> int:
    if not isinstance(dollar_amount, Decimal):
        raise TypeError(f"Expected type Decimal, got {type(dollar_amount)}")

    cents = int(dollar_amount * 100)
    print(f"dollars to cents: {dollar_amount} -> {cents}")
    return cents





def str_to_date_obj(due_date: int) -> date:
    due_date = int(due_date)
    current_date = datetime.today()
    try:
        if current_date.day <= due_date:  # Bill due this month

            # create due date object with due date being this month
            due_date_obj: date = date(current_date.year, current_date.month, due_date)
            date_difference = due_date_obj - current_date

        elif current_date.day > due_date:  # Bill due next month (add month to date object)

            # add month to current month
            if current_date.month == 12:  # if current month is 12, set to january
                due_date_obj = date(current_date.year, 1, due_date)

            # current month is less than 12
            else:
                due_date_obj = date(current_date.year, current_date.month + 1, due_date)

            return due_date_obj
    except ValueError:
        return {"message": "Date you entered for month was not valid."}, 404
