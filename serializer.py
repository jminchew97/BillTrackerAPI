class Serialize:
    """ Class that allows you to convert lists returned from SQLITE into python DICT"""

    # add keys that will be matched up to values in list from DB
    def __init__(self, keys: tuple, db_list: list) -> None:
        self.db_list = db_list
        self.keywords: list = keys
        self.converted_dict: dict = {}

        """ Enter in as many key words, make sure they correspond to each value in list """
        # error handling

        # get list one from db_list to see length of one row
        db_row = self.db_list[0]
        if len(self.keywords) > len(db_row): # enters more keywords than there are values in db_list
            raise RuntimeError(f"""ERROR: You entered {len(self.keywords)} keys, when there were {len(db_row)} values in the
           database list. Make sure KEY:VALUES match.""")

        elif len(self.keywords) < len(db_row): # more values in db_list than there are keywords
            raise RuntimeError(f"""ERROR: You entered {len(db_row)} keys, when there were {len(self.keywords)} values in the
                       database list. Make sure KEY:VALUES match.""")

        # db_list/values example= [
        # [1,"electric",200,"06-10-14"],
        # [2,"water",300,"06-10-14"],
        # [3,"gas",400,"06-10-14"]
        # ]
        #
        # Iterates through list and
        for x in range(0, len(self.db_list)):
            # get primary key
            primary_key = self.db_list[x][0]  # ex. 1, 2 etc..

            self.converted_dict[primary_key] = dict(zip(self.keywords, self.db_list[x]))
        # example of serialized data below once finished with loop

        # "1": {
        #     "amount": 2.0,
        #     "bill_id": 1,
        #     "bill_name": "Internet",
        #     "due_date": "2023-02-09"
        # },
        # "2": {
        #     "amount": 2.0,
        #     "bill_id": 1,
        #     "bill_name": "Internet",
        #     "due_date": "2023-02-09"
        # }

    # print all keywords added
    def print_keywords(self):
        """Prints keywords entered at objects creation"""
        for x in self.keywords:
            print(x)

    # print dictionary converted from list
    def get(self):
        """Get the serialized data as a dictionary"""
        return self.converted_dict
