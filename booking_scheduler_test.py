from datetime import datetime

from booking_scheduler import BookingScheduler


class SundayBookingScheduler(BookingScheduler):
    def __init__(self, capacity_per_hour):
        super().__init__(capacity_per_hour)

    def get_now(self):
        return datetime.strptime("2022-09-18 18:00", "%Y-%m-%d %H:%M")


class MondayBookingScheduler(BookingScheduler):
    def __init__(self, capacity_per_hour):
        super().__init__(capacity_per_hour)

    def get_now(self):
        return datetime.strptime("2022-09-19 18:00", "%Y-%m-%d %H:%M")
