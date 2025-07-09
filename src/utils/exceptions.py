class BaseException(Exception):
    """
    Базовы класс ошибки
    """

    def __init__(
        self,
        msg: str,
        code: int,
        data: dict | None,
        *args: object,
    ) -> None:
        self.msg = msg
        self.code = code
        self.data = data
        super().__init__(*args)

    def __repr__(self) -> str:
        return f"{self.msg}: {self.code}"

    def __str__(self) -> str:
        return self.__repr__()


class DataExeption(BaseException):
    """
    Ошибка вызываеться если пользователь предоставил
    не верные данные
    """

    def __init__(
        self,
        msg: str,
        code: int = 400,
        data: dict | None = None,
        *args: object,
    ) -> None:
        super().__init__(msg, code, data, *args)


class AccessExeption(BaseException):
    """
    Ошибка вызываеться если доступ ресурсу запрещен
    или действие не доступно согласно роли пользователя
    """

    def __init__(
        self,
        msg: str,
        code: int = 403,
        data: dict | None = None,
        *args: object,
    ) -> None:
        super().__init__(msg, code, data, *args)


class NotFoundException(BaseException):
    """
    Ошибка вызываеться если чкакие то данные не найдены
    """

    def __init__(
        self,
        msg: str,
        code: int = 404,
        data: dict | None = None,
        *args: object,
    ) -> None:
        super().__init__(msg, code, data, *args)


class APIException(BaseException):
    """
    Ошибка вызываеться если произошла с внешним апи
    """

    def __init__(
        self,
        msg: str,
        code: int = 409,
        data: dict | None = None,
        *args: object,
    ) -> None:
        super().__init__(msg, code, data, *args)


class CoreException(BaseException):
    """
    Ошибка вызываеться если произошла какая то внутренная ошибка
    """

    def __init__(
        self,
        msg: str,
        code: int = 500,
        data: dict | None = None,
        *args: object,
    ) -> None:
        super().__init__(msg, code, data, *args)
