from abc import ABC, abstractmethod

from data_handler import *


class BillAPI(ABC):

    @abstractmethod
    def create_bill(self, new_bill: BillCreate) -> str:
        pass

    @abstractmethod
    def get_all_bills(self) -> list[tuple[object]]:
        pass

    @abstractmethod
    def get_bill_by_id(self, id: str):
        pass

    @abstractmethod
    def delete_bill_by_id(self, id: str) -> dict:
        pass

    @abstractmethod
    def update_bill(self, id: str, edited_bill: Bill) -> Bill:
        pass

