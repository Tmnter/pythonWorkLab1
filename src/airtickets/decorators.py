from functools import wraps
from typing import Any, Callable


def validated(**rules: str) -> Callable:
    """Декоратор із параметрами для валідації іменованих аргументів."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Збираємо всі аргументи (позиційні та іменовані) в один словник
            code = func.__code__
            arg_names = code.co_varnames[:code.co_argcount]
            all_args = dict(zip(arg_names, args))
            all_args.update(kwargs)

            for arg_name, rule in rules.items():
                if arg_name in all_args:
                    val = all_args[arg_name]

                    # 1. Правило "positive"
                    if rule == "positive":
                        if not isinstance(val, (int, float)) or val <= 0:
                            raise ValueError(
                                f"Аргумент '{arg_name}' порушує правило 'positive': має бути числом > 0, отримано {val}."
                            )

                    # 2. Правило "non_empty"
                    elif rule == "non_empty":
                        if not isinstance(val, str) or not val.strip():
                            raise ValueError(
                                f"Аргумент '{arg_name}' порушує правило 'non_empty': має бути непорожнім рядком."
                            )

                    # 3. Правило "one_of:a,b,c"
                    elif rule.startswith("one_of:"):
                        allowed_str = rule.split(":", 1)[1]
                        allowed_values = [item.strip() for item in allowed_str.split(",")]
                        if str(val) not in allowed_values:
                            raise ValueError(
                                f"Аргумент '{arg_name}' порушує правило '{rule}': значення '{val}' не належить множині {allowed_values}."
                            )

                    else:
                        raise ValueError(f"Невідоме правило валідації: '{rule}'")

            return func(*args, **kwargs)

        return wrapper

    return decorator