import unittest
from datetime import datetime, timedelta
from unittest import TestCase
from unittest.mock import Mock, patch

from booking_scheduler import BookingScheduler
from schedule import Schedule

NOT_ON_HOUR = datetime.strptime("1993-05-16 09:18", "%Y-%m-%d %H:%M")
ON_THE_HOUR = datetime.strptime("2008-09-18 16:00", "%Y-%m-%d %H:%M")

SATURDAY_GOLDEN_HOUR = datetime.strptime("2022-09-17 19:00", "%Y-%m-%d %H:%M")
SUNDAY_GOLDEN_HOUR = datetime.strptime("2022-09-18 19:00", "%Y-%m-%d %H:%M")

CUSTOMER_WITHOUT_MAIL = Mock()
CUSTOMER_WITHOUT_MAIL.get_email.return_value = None

CUSTOMER_WITH_MAIL = Mock()
CUSTOMER_WITH_MAIL.get_email.return_value = "hello@world.com"

UNDER_CAPA = 1
CAPA_PER_HOUR = 3


class TestBookingScheduler(TestCase):
    def setUp(self):
        self.booking_scheduler = BookingScheduler(CAPA_PER_HOUR)
        self.sms_sender = Mock()
        self.booking_scheduler.set_sms_sender(self.sms_sender)
        self.mail_sender = Mock()
        self.booking_scheduler.set_mail_sender(self.mail_sender)

    def test_예약은_정시에만_가능하다_정시가_아닌경우_예약불가(self):
        schedule = Schedule(NOT_ON_HOUR, UNDER_CAPA, CUSTOMER_WITHOUT_MAIL)

        with self.assertRaises(ValueError):
            self.booking_scheduler.add_schedule(schedule)

    def test_예약은_정시에만_가능하다_정시인_경우_예약가능(self):
        schedule = Schedule(ON_THE_HOUR, UNDER_CAPA, CUSTOMER_WITHOUT_MAIL)

        self.booking_scheduler.add_schedule(schedule)

        self.assertTrue(self.booking_scheduler.has_schedule(schedule))

    def test_시간대별_인원제한이_있다_같은_시간대에_Capacity_초과할_경우_예외발생(self):
        full_capa_schedule = Schedule(ON_THE_HOUR, number_of_people=CAPA_PER_HOUR, customer=CUSTOMER_WITHOUT_MAIL)
        self.booking_scheduler.add_schedule(full_capa_schedule)

        another_schedule = Schedule(ON_THE_HOUR, UNDER_CAPA, CUSTOMER_WITHOUT_MAIL)
        with self.assertRaises(ValueError) as context:
            self.booking_scheduler.add_schedule(another_schedule)

        self.assertEqual("Number of people is over restaurant capacity per hour", str(context.exception))

    def test_시간대별_인원제한이_있다_같은_시간대가_다르면_Capacity_차있어도_스케쥴_추가_성공(self):
        full_capa_schedule = Schedule(ON_THE_HOUR, number_of_people=CAPA_PER_HOUR, customer=CUSTOMER_WITHOUT_MAIL)
        self.booking_scheduler.add_schedule(full_capa_schedule)

        another_datetime = ON_THE_HOUR + timedelta(hours=1)
        another_schedule = Schedule(another_datetime, UNDER_CAPA, CUSTOMER_WITHOUT_MAIL)
        self.booking_scheduler.add_schedule(another_schedule)

        self.assertTrue(self.booking_scheduler.has_schedule(another_schedule))

    def test_예약완료시_SMS는_무조건_발송(self):
        schedule = Schedule(ON_THE_HOUR, UNDER_CAPA, CUSTOMER_WITHOUT_MAIL)
        self.booking_scheduler.add_schedule(schedule)

        self.sms_sender.send.assert_called()

    def test_이메일이_없는_경우에는_이메일_미발송(self):
        schedule = Schedule(ON_THE_HOUR, UNDER_CAPA, CUSTOMER_WITHOUT_MAIL)
        self.booking_scheduler.add_schedule(schedule)

        self.mail_sender.send_mail.assert_not_called()

    def test_이메일이_있는_경우에는_이메일_발송(self):
        schedule = Schedule(ON_THE_HOUR, UNDER_CAPA, customer=CUSTOMER_WITH_MAIL)
        self.booking_scheduler.add_schedule(schedule)

        self.mail_sender.send_mail.assert_called()

    @patch.object(BookingScheduler, 'get_now', return_value=SUNDAY_GOLDEN_HOUR)
    def test_현재날짜가_일요일인_경우_예약불가_예외처리(self, mock):
        schedule = Schedule(ON_THE_HOUR, UNDER_CAPA, CUSTOMER_WITHOUT_MAIL)

        with self.assertRaises(ValueError):
            self.booking_scheduler.add_schedule(schedule)

    @patch.object(BookingScheduler, 'get_now', return_value=SATURDAY_GOLDEN_HOUR)
    def test_현재날짜가_일요일이_아닌경우_예약가능(self, mock):
        schedule = Schedule(ON_THE_HOUR, UNDER_CAPA, CUSTOMER_WITHOUT_MAIL)
        self.booking_scheduler.add_schedule(schedule)

        self.assertTrue(self.booking_scheduler.has_schedule(schedule))


if __name__ == '__main__':  # 이거 없으면 커버리지 안 나옴?
    unittest.main()
