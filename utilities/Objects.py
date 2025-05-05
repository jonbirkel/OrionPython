import json

class Objects:
    def __init__(self, **overrides):
        """Creates a BillInstanceObject with default values, allowing overrides."""
        self.BillInstanceObject = {
            "nickName": "",
            "dateRange": None,
            "runFor": 0,
            "keys": [],
            "asOfDate": "12/31/2024",
            "billType": 1,
            "vHint": 5,
            "pkKey": None,
            "endDateOverride": None,
            "recurringAdjustmentOverride": False,
            "acctList": None,
            "valueAsOfOverride": None,
            "isMockBill": True,
            "IncludeCashFlow": True,
            "allowDuplicateMockBills": True,
            "runForAccounts": 1,
            "isFinalBill": False,
            "isLockdown": False
        }

        # Override defaults if any were provided
        self.BillInstanceObject.update(overrides)

    @classmethod
    def BillInstance(cls, **kwargs):
        """Alternative way to create an instance using Objects.BillInstance(...)"""
        return cls(**kwargs)

    def to_json(self):
        """Returns the JSON string representation of the object."""
        return json.dumps(self.BillInstanceObject, indent=4)

    # def __init__(self, **overrides):
    #     """Creates a HH/Reg/Account Object with default values, allowing overrides."""
    #     self.NewHouseholdObject =

