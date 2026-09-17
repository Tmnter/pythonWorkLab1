from typing import Any, Iterable, Iterator, List, Union

from .decorators import validated
from .entities import Ticket
from .errors import DomainError
from .values import Money

class EntityNotFound(DomainError):
    """Виникає, коли сутність не знайдено в колекції."""
    pass


class FlightIterator:
    """3.2. Ітератор простого абосторінкового обходу колекції Flight."""

    def __init__(self, flight: "Flight", page_size: int) -> None:
        if page_size <= 0:
            raise ValueError("Розмір сторінки page_size повинен бути більшим за 0.")
        self._flight = flight
        self._page_size = page_size
        self._current_index = 0

    def __iter__(self) -> "FlightIterator":
        return self

    def __next__(self) -> List[Ticket]:
        if self._current_index >= len(self._flight):
            raise StopIteration

        page = []
        for _ in range(self._page_size):
            if self._current_index < len(self._flight):
                # Звертаємося до __getitem__ самої колекції
                page.append(self._flight[self._current_index])
                self._current_index += 1
            else:
                break
        return page


class Flight:
    @validated(passenger="non_empty", seat_class="one_of:economy,business,first", price_amount="positive")
    def create_and_add_ticket(self, *, passenger: str, seat_class: str, price_amount: float) -> Ticket:
        """Створення та додавання нових квитків безпосередньо через рейс."""
        ticket = Ticket(passenger, self.flight_number, seat_class, Money("USD", price_amount))
        self.add_ticket(ticket)
        return ticket
    ALLOWED_KWARGS = {"seat_class", "passenger", "price_max"}

    def __init__(self, flight_number: str, tickets: Iterable[Ticket] = ()) -> None:
        self.flight_number = flight_number
        self._items: List[Ticket] = list(tickets)
        # Індекс у вигляді словника для швидкого пошуку у стилі EAFP
        self._index: dict[str, Ticket] = {}
        for ticket in self._items:
            self._update_index(ticket)

    def _update_index(self, ticket: Ticket) -> None:
        # Унікальний ідентифікатор квитка: "PassengerName_SeatClass"
        key = f"{ticket.passenger}_{ticket.seat_class}"
        self._index[key] = ticket

    def add_ticket(self, ticket: Ticket) -> None:
        self._items.append(ticket)
        self._update_index(ticket)

    # --- 3.1. Протокол послідовності ---
    def __len__(self) -> int:
        return len(self._items)

    def __getitem__(self, item: Union[int, slice]) -> Union[Ticket, "Flight"]:
        if isinstance(item, slice):
            # Повертає новий екземпляр колекції того самого типу (не список!)
            return Flight(self.flight_number, self._items[item])
        return self._items[item]

    def __contains__(self, item: Any) -> bool:
        if isinstance(item, Ticket):
            key = f"{item.passenger}_{item.seat_class}"
            return key in self._index
        elif isinstance(item, str):
            return item in self._index
        return False

    def __iter__(self) -> Iterator[Ticket]:
        return iter(self._items)

    # --- 3.2. Посторінковий обхід ---
    def pages(self, page_size: int) -> FlightIterator:
        return FlightIterator(self, page_size)

    # --- 3.3. Екземпляр колекції як запит (__call__) ---
    def __call__(self, **kwargs: Any) -> "Flight":
        # Перевірка на невідомі критерії
        unknown_args = set(kwargs.keys()) - self.ALLOWED_KWARGS
        if unknown_args:
            raise TypeError(
                f"Невідомі критерії запиту: {list(unknown_args)}. "
                f"Припустимі критерії: {list(self.ALLOWED_KWARGS)}"
            )

        filtered = self._items

        if "seat_class" in kwargs:
            target_class = str(kwargs["seat_class"]).lower()
            filtered = [t for t in filtered if t.seat_class == target_class]

        if "passenger" in kwargs:
            target_pass = str(kwargs["passenger"]).lower()
            filtered = [t for t in filtered if target_pass in t.passenger.lower()]

        if "price_max" in kwargs:
            max_p = float(kwargs["price_max"])
            filtered = [t for t in filtered if t.price.amount <= max_p]

        # Повертає новий екземпляр колекції
        return Flight(self.flight_number, filtered)

    # --- 3.4. Пошук за ідентифікатором у стилі EAFP ---
    def get(self, entity_id: str) -> Ticket:
        try:
            return self._index[entity_id]
        except KeyError:
            raise EntityNotFound(f"Квиток з ідентифікатором '{entity_id}' не знайдено.") from None

    def __repr__(self) -> str:
        return f"Flight(number='{self.flight_number}', tickets_count={len(self)})"

    def __add__(self, other: Any) -> "Flight":
        if not isinstance(other, Flight):
            return NotImplemented

        # Об'єднуємо квитки без дублікатів за унікальним ідентифікатором
        combined_tickets = list(self._items)
        existing_keys = {f"{t.passenger}_{t.seat_class}" for t in self._items}

        for ticket in other._items:
            key = f"{ticket.passenger}_{ticket.seat_class}"
            if key not in existing_keys:
                combined_tickets.append(ticket)
                existing_keys.add(key)

        return Flight(self.flight_number, combined_tickets)

    def __radd__(self, other: Any) -> "Flight":
        # Коли sum() починає обхід із 0 (int)
        if other == 0:
            return Flight(self.flight_number, self._items)
        if isinstance(other, Flight):
            return other.__add__(self)
        return NotImplemented