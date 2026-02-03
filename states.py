from aiogram.fsm.state import StatesGroup, State


class Register(StatesGroup):
    language = State()
    full_name = State()
    phone_number = State()


class RentStatus(StatesGroup):
    product_choice = State()
    lesa_size_choice = State()
    taxta_size_choice = State()
    metal_size_choice = State()
    quantity = State()
    additional_choice = State()
    renter_fullname = State()
    renter_phone_number = State()
    renter_passport_info = State()
    date_mode = State()
    start_date = State()
    end_date = State()
    location_request = State()
    notes = State()


class ReturnProduct(StatesGroup):
    choosing_renter = State()
    choosing_product = State()
    entering_quantity = State()
    confirming = State()


class ReportState(StatesGroup):
    get_start_end_dates= State()
    send_report = State()
