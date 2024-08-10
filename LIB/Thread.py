import threading
from typing import Any, Callable

class Thread:
    def __init__(self, function: Callable[..., Any], *args, **kwargs) -> None:
        self.__function = lambda: function(*args, **kwargs)
        self.__return_value = None
        self.__exception = None
        self.__completed = threading.Event()
        self.__thread = threading.Thread(target=self.__background_function, name=function.__name__)
        self.__thread.start()

    def __del__(self) -> None:
        if not self.__completed.is_set():
            self.__thread.join()

    def __background_function(self) -> None:
        try:
            self.__return_value = self.__function()
        except Exception as e:
            self.__exception = e
        finally:
            self.__completed.set()

    def result(self, timeout: float = None) -> Any:
        if not self.__completed.wait(timeout):
            raise TimeoutError("Function execution timed out")
        if self.__exception:
            raise self.__exception
        return self.__return_value

    @property
    def completed(self) -> bool:
        return self.__completed.is_set()