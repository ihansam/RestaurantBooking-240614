from communication import SmsSender


class TestableSmsSender(SmsSender):
    def __init__(self):
        self.__is_send_called = False

    def send(self, schedule):
        print(f"{self.__class__.__name__}에서 send() 실행")
        self.__is_send_called = True

    def is_send_method_called(self):
        return self.__is_send_called
