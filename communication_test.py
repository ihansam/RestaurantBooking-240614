from communication import SmsSender, MailSender


class TestableSmsSender(SmsSender):
    def __init__(self):
        self.__is_send_called = False

    def send(self, schedule):
        print(f"{self.__class__.__name__}에서 send() 실행")
        self.__is_send_called = True

    def is_send_method_called(self):
        return self.__is_send_called


class TestableMailSender(MailSender):
    def __init__(self):
        self.__send_called_count = 0

    def send_mail(self, schedule):
        self.__send_called_count += 1

    def get_count_send_mail_is_called(self):
        return self.__send_called_count
