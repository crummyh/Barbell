from typing import TypeVar

T = TypeVar("T")

def validated(model: type[T], obj: object) -> T:
    return model.model_validate(obj)  # type: ignore
