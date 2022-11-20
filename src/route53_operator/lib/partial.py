"""Partial.make_optional is used to convert a Pydantic model's fields to optional fields.

This is used to turn schemas into partial schemas, which are used to update records."""
# https://github.com/pydantic/pydantic/issues/1223
# https://github.com/pydantic/pydantic/pull/3179
# Todo migrate to pydanticv2 partial
import inspect

from pydantic import BaseModel


def make_optional(*fields):
    """Class decorator to make fields optional"""

    def dec(_cls):
        for field in fields:
            _cls.__fields__[field].required = False
        return _cls

    if fields and inspect.isclass(fields[0]) and issubclass(fields[0], BaseModel):
        cls = fields[0]
        fields = cls.__fields__
        return dec(cls)
    return dec
