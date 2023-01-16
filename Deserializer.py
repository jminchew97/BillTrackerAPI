from typing import TypeVar
from dataclasses import dataclass, fields
from decimal import Decimal
import datetime


@dataclass
class Bill:
    id: int
    name: str
    amount: Decimal
    due_date: datetime.date


T = TypeVar('T')


#                   (any type)    (list)
def deserialize_row(typ: type[T], row: list[object]) -> T:
    # set bill properties here
    # create datetime.date object

    date = datetime.datetime.strptime(row[3], "%Y-%m-%d").date()

    #               id      name    amount  date
    new_bill = Bill(row[0], row[1], row[2], date)

    return [new_bill]


def deserialize_rows(typ: type[T], rows: list[list[object]]) -> list[T]:
    return [deserialize_row(typ, row) for row in rows]


# Example
rows = [[1, 'Water', '20.00', '2023-01-31'], [2, 'Electric', '50.00', '2023-02-20']]
bills = deserialize_rows(Bill, rows)
