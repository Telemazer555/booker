from pydantic import BaseModel, Field
from typing import Optional
import json
import os
import dotenv
from faker import Faker

fake = Faker()

dotenv.load_dotenv()
HEADERS = os.environ.get('HEADERS')
HEADERS = json.loads(HEADERS)
BASE_URL = os.environ.get('BASE_URL')
JSON_BODY = os.environ.get('JSON_BODY')
JSON_BODY = json.loads(JSON_BODY)


class BookingDates(BaseModel):
    checkin: str
    checkout: str

    @classmethod
    def fake_checkdates(cls):
        return cls(
            checkin=fake.date(),
            checkout=fake.date()
        )


class BaseBookingSchema(BaseModel):
    firstname: str
    lastname: str
    totalprice: int
    depositpaid: bool
    bookingdates: dict
    bookingdates: BookingDates
    additionalneeds: Optional[str] = None


class BookingResponseData(BaseModel):
    firstname: str = Field(default_factory=fake.first_name)
    lastname: str = Field(default_factory=fake.last_name)
    totalprice: int = Field(default_factory=lambda: fake.random_int(min=100, max=10000))
    depositpaid: bool = Field(default_factory=fake.boolean)
    bookingdates: BookingDates = Field(default_factory=BookingDates.fake_checkdates)
    additionalneeds: str | None = Field(
        default_factory=lambda: fake.random_element(elements=("breakfast", "dinner", "supper", None))
    )


class UserSchema2(BaseModel):
    bookingid: int
    booking: BaseBookingSchema


class UpdateBookingSchema(BaseBookingSchema):
    firstname: str
    lastname: str
    totalprice: int
    depositpaid: bool
    bookingdates: BookingDates
    additionalneeds: Optional[str] = None
