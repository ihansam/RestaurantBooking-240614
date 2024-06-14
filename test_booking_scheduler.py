import unittest
from datetime import datetime, timedelta
from unittest import TestCase

from booking_scheduler import BookingScheduler
from communication_test import TestableSmsSender, TestableMailSender
from schedule import Customer, Schedule

NOT_ON_HOUR = datetime.strptime("1993-05-16 09:18", "%Y-%m-%d %H:%M")
ON_THE_HOUR = datetime.strptime("2022-09-18 19:00", "%Y-%m-%d %H:%M")
CUSTOMER = Customer("fake name", "010-1234-5678")
CUSTOMER_WITH_MAIL = Customer("Fake Name", "010-1234-5678", "hello.world@com")

UNDER_CAPA = 1
CAPA_PER_HOUR = 3


class TestableBookingScheduler(BookingScheduler):
    def __init__(self, capacity_per_hour, date_time: str):
        super().__init__(capacity_per_hour)
        self._datetime = date_time

    def get_now(self):
        return datetime.strptime(self._datetime, "%Y-%m-%d %H:%M")


class TestBookingScheduler(TestCase):
    def setUp(self):
        self.booking_scheduler = BookingScheduler(CAPA_PER_HOUR)
        self.testable_sms_sender = TestableSmsSender()
        self.booking_scheduler.set_sms_sender(self.testable_sms_sender)
        self.testable_mail_sender = TestableMailSender()
        self.booking_scheduler.set_mail_sender(self.testable_mail_sender)

    def test_예약은_정시에만_가능하다_정시가_아닌경우_예약불가(self):
        schedule = Schedule(NOT_ON_HOUR, UNDER_CAPA, CUSTOMER)

        with self.assertRaises(ValueError):
            self.booking_scheduler.add_schedule(schedule)

    def test_예약은_정시에만_가능하다_정시인_경우_예약가능(self):
        schedule = Schedule(ON_THE_HOUR, UNDER_CAPA, CUSTOMER)

        self.booking_scheduler.add_schedule(schedule)

        self.assertTrue(self.booking_scheduler.has_schedule(schedule))

    def test_시간대별_인원제한이_있다_같은_시간대에_Capacity_초과할_경우_예외발생(self):
        full_capa_schedule = Schedule(ON_THE_HOUR, number_of_people=CAPA_PER_HOUR, customer=CUSTOMER)
        self.booking_scheduler.add_schedule(full_capa_schedule)

        another_schedule = Schedule(ON_THE_HOUR, UNDER_CAPA, CUSTOMER)
        with self.assertRaises(ValueError) as context:
            self.booking_scheduler.add_schedule(another_schedule)

        self.assertEqual("Number of people is over restaurant capacity per hour", str(context.exception))

    def test_시간대별_인원제한이_있다_같은_시간대가_다르면_Capacity_차있어도_스케쥴_추가_성공(self):
        full_capa_schedule = Schedule(ON_THE_HOUR, number_of_people=CAPA_PER_HOUR, customer=CUSTOMER)
        self.booking_scheduler.add_schedule(full_capa_schedule)

        another_datetime = ON_THE_HOUR + timedelta(hours=1)
        another_schedule = Schedule(another_datetime, UNDER_CAPA, CUSTOMER)
        self.booking_scheduler.add_schedule(another_schedule)

        self.assertTrue(self.booking_scheduler.has_schedule(another_schedule))

    def test_예약완료시_SMS는_무조건_발송(self):
        schedule = Schedule(ON_THE_HOUR, UNDER_CAPA, CUSTOMER)
        self.booking_scheduler.add_schedule(schedule)

        self.assertTrue(self.testable_sms_sender.is_send_method_called())

    def test_이메일이_없는_경우에는_이메일_미발송(self):
        schedule = Schedule(ON_THE_HOUR, UNDER_CAPA, CUSTOMER)
        self.booking_scheduler.add_schedule(schedule)

        self.assertEqual(0, self.testable_mail_sender.get_count_send_mail_is_called())

    def test_이메일이_있는_경우에는_이메일_발송(self):
        schedule = Schedule(ON_THE_HOUR, UNDER_CAPA, customer=CUSTOMER_WITH_MAIL)
        self.booking_scheduler.add_schedule(schedule)

        self.assertEqual(1, self.testable_mail_sender.get_count_send_mail_is_called())

    def test_현재날짜가_일요일인_경우_예약불가_예외처리(self):
        self.booking_scheduler = TestableBookingScheduler(CAPA_PER_HOUR, "2022-09-18 19:00")

        schedule = Schedule(ON_THE_HOUR, UNDER_CAPA, CUSTOMER)

        with self.assertRaises(ValueError):
            self.booking_scheduler.add_schedule(schedule)

    def test_현재날짜가_일요일이_아닌경우_예약가능(self):
        self.booking_scheduler = TestableBookingScheduler(CAPA_PER_HOUR, "2022-09-17 19:00")

        schedule = Schedule(ON_THE_HOUR, UNDER_CAPA, CUSTOMER)
        self.booking_scheduler.add_schedule(schedule)

        self.assertTrue(self.booking_scheduler.has_schedule(schedule))


if __name__ == '__main__':  # 이거 없으면 커버리지 안 나옴?
    unittest.main()
