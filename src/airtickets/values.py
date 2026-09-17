from functools import total_ordering
from typing import Any, Tuple
from typing import Union


@total_ordering
class Money:
    # 1.1. Визначаємо __slots__ з полями та прапорцем _frozen
    __slots__ = ("currency", "amount", "_frozen")

    def __init__(self, currency: str, amount: float) -> None:
        # Валідація типів і значень (базова перевірка)
        if not isinstance(currency, str) or not currency:
            raise ValueError("Currency must be a non-empty string")
        if not isinstance(amount, (int, float)) or amount <= 0:
            raise ValueError("Amount must be a positive number")

        # Встановлюємо значення через object.__setattr__, щоб оминути власну заборону
        object.__setattr__(self, "currency", currency)
        object.__setattr__(self, "amount", float(amount))

        # Встановлюємо прапорець незмінності наприкінці __init__
        object.__setattr__(self, "_frozen", True)

    def __setattr__(self, name: str, value: Any) -> None:
        # Забороняємо будь-яку зміну атрибутів після завершення __init__
        if getattr(self, "_frozen", False):
            raise AttributeError(f"Об'єкт Money є незмінним (immutable). Спроба змінити '{name}'")
        object.__setattr__(self, name, value)

    # 1.3. Рядкові подання
    def __repr__(self) -> str:
        return f"Money(currency='{self.currency}', amount={self.amount})"

    def __str__(self) -> str:
        return f"{self.amount:.2f} {self.currency}"

    # Допоміжний метод для зручного отримання кортежу полів
    def _as_tuple(self) -> Tuple[str, float]:
        return (self.currency, self.amount)

    # 1.4. Порівняння та впорядкування
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self._as_tuple() == other._as_tuple()

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise TypeError(f"Неможливо порівняти грошові суми з різними валютами: {self.currency} та {other.currency}")
        return self.amount < other.amount

    # 1.5. Хешованість (узгоджено з __eq__)
    def __hash__(self) -> int:
        return hash(self._as_tuple())

    def __add__(self, other: Any) -> "Money":
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise ValueError(
                f"Неможливо додати несумісні валюти: '{self.currency}' та '{other.currency}'."
            )
        return Money(self.currency, self.amount + other.amount)

    def __sub__(self, other: Any) -> "Money":
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise ValueError(
                f"Неможливо відняти несумісні валюти: '{self.currency}' та '{other.currency}'."
            )
        new_amount = self.amount - other.amount
        if new_amount <= 0:
            raise ValueError("Результат віднімання ціни повинен бути більшим за 0.")
        return Money(self.currency, new_amount)

    def __mul__(self, other: Union[int, float]) -> "Money":
        if not isinstance(other, (int, float)):
            return NotImplemented
        return Money(self.currency, self.amount * other)

    def __rmul__(self, other: Union[int, float]) -> "Money":
        return self.__mul__(other)