"""Логика сигналов о цене. Не зависит от сети, поэтому легко тестируется."""
from dataclasses import dataclass, field


@dataclass
class Rule:
    symbol: str
    above: float | None = None
    below: float | None = None
    # какие условия уже сработали и ещё не «сбросились» (цена не вернулась обратно)
    active: set[str] = field(default_factory=set)

    @classmethod
    def from_dict(cls, data: dict) -> "Rule":
        rule = cls(symbol=data["symbol"].upper(), above=data.get("above"), below=data.get("below"))
        if rule.above is None and rule.below is None:
            raise ValueError(f"Для {rule.symbol} не задано ни above, ни below")
        if rule.above is not None and rule.below is not None and rule.below >= rule.above:
            raise ValueError(f"Для {rule.symbol} значение below должно быть меньше above")
        return rule


def check(rule: Rule, price: float) -> list[str]:
    """Возвращает сообщения для сработавших условий.

    Сигнал приходит один раз при пересечении уровня. Пока цена остаётся за уровнем,
    повторов нет. Когда цена вернулась обратно, условие снова «заряжено».
    """
    messages = []
    for name, hit in (
        ("above", rule.above is not None and price >= rule.above),
        ("below", rule.below is not None and price <= rule.below),
    ):
        if hit and name not in rule.active:
            rule.active.add(name)
            level = rule.above if name == "above" else rule.below
            word = "выше" if name == "above" else "ниже"
            messages.append(f"{rule.symbol}: цена {price:g} {word} уровня {level:g}")
        elif not hit:
            rule.active.discard(name)
    return messages
