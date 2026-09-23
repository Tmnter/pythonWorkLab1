import copy
from typing import Any, Optional, Type
from collections_ import Flight


class FlightBookingSession:
    """Контекстний менеджер для атомарних пакетних змін над колекцією Flight."""

    def __init__(self, flight: Flight) -> None:
        self.flight = flight
        self._snapshot: Optional[Flight] = None

    def __enter__(self) -> Flight:
        self._snapshot = copy.deepcopy(self.flight)
        return self.flight

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Any
    ) -> bool:
        if exc_type is not None:
            # Якщо виник виняток — відновлюємо стан колекції зі знімка
            if self._snapshot is not None:
                self.flight._items = self._snapshot._items
                self.flight._index = self._snapshot._index
            # Повертаємо False: виняток НЕ приховується та прокидається вище
            return False

        # У разі успіху зміни зберігаються
        return True