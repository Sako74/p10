# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.


class BookingDetails:
    def __init__(
        self,
        from_city: str = "",
        to_city: str = "",
        from_dt: str = "",
        to_dt: str = "",
        budget: str = ""
    ):
        self.from_city = from_city
        self.to_city = to_city
        self.from_dt = from_dt
        self.to_dt = to_dt
        self.budget = budget
