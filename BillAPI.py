from abc import ABC, abstractmethod

from data_handler import *


class BillAPI(ABC):

    @abstractmethod
    def create_bill(self, new_bill: BillNoID) -> str:
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
    def edit_bill_by_id(self, id: str) -> Bill:
        pass
