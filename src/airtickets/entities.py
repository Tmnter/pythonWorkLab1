import re
from typing import Any, Dict

from .values import Money
from .decorators import validated
class Ticket:
    @validated(new_passenger="non_empty", new_class="one_of:economy,business,first")
    def rebook(self, *, new_passenger: str, new_class: str) -> None:
        """Перебронювання квитка на нового пасажира та клас."""
        self.passenger = new_passenger
        self.seat_class = new_class
    # Множина припустимих класів обслуговування (варіант 15)
    ALLOWED_CLASSES = {"economy", "business", "first"}

    def __init__(self, passenger: str, flight_no: str, seat_class: str, price: Money) -> None:
        # Присвоєння відбувається через сетери для спрацювання валідації
        self.passenger = passenger
        self.flight_no = flight_no
        self.seat_class = seat_class
        self.price = price

    # 2.1. Валідація полів через property
    @property
    def passenger(self) -> str:
        return self._passenger

    @passenger.setter
    def passenger(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Ім'я пасажира не може бути порожнім рядком.")
        self._passenger = value.strip()

    @property
    def flight_no(self) -> str:
        return self._flight_no

    @flight_no.setter
    def flight_no(self, value: str) -> None:
        if not self.is_valid_flight_no(value):
            raise ValueError(f"Некоректний номер рейсу: '{value}'. Формат має бути на кшталт 'PS-123' або 'UA777'.")
        self._flight_no = value.strip().upper()

    @property
    def seat_class(self) -> str:
        return self._seat_class

    @seat_class.setter
    def seat_class(self, value: str) -> None:
        val = value.lower() if isinstance(value, str) else ""
        if val not in self.ALLOWED_CLASSES:
            raise ValueError(
                f"Некоректний клас сидіння: '{value}'. "
                f"Дозволені значення: {', '.join(sorted(self.ALLOWED_CLASSES))}."
            )
        self._seat_class = val

    @property
    def price(self) -> Money:
        return self._price

    @price.setter
    def price(self, value: Money) -> None:
        if not isinstance(value, Money):
            raise ValueError("Поле price має бути екземпляром класу Money.")
        if value.amount <= 0:
            raise ValueError(f"Ціна квитка має бути більшою за 0 (отримано {value.amount}).")
        self._price = value

    # 2.2. Статичний метод та метод класу
    @staticmethod
    def is_valid_flight_no(value: str) -> bool:
        """Перевірка формату номера рейсу (наприклад, 2-3 літери, дефіс/пробіл за бажанням, та 1-4 цифри)."""
        if not isinstance(value, str):
            return False
        pattern = r"^[A-Za-z]{2,3}-?\d{1,4}$"
        return bool(re.match(pattern, value.strip()))

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Ticket":
        """Створює сутність зі словника «сирих» значень."""
        # Створюємо об'єкт Money із закладених даних
        price_data = data.get("price")
        if isinstance(price_data, dict):
            money_obj = Money(price_data.get("currency", ""), price_data.get("amount", 0))
        elif isinstance(price_data, Money):
            money_obj = price_data
        else:
            raise ValueError("Дані про ціну у словнику повинні містити 'currency' та 'amount'.")

        return cls(
            passenger=data.get("passenger", ""),
            flight_no=data.get("flight_no", ""),
            seat_class=data.get("seat_class", ""),
            price=money_obj,
        )

    def __repr__(self) -> str:
        return (
            f"Ticket(passenger='{self.passenger}', flight_no='{self.flight_no}', "
            f"seat_class='{self.seat_class}', price={self.price!r})"
        )
