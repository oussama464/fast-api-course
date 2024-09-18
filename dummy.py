from functools import cached_property
from math import pi

from pydantic import BaseModel, Field, ValidationError, computed_field


class Circle(BaseModel):
    center: tuple[int, int] = Field(default=(0, 0), repr=False)
    radius: int = Field(default=1, gt=0)

    @computed_field(alias="AREA")
    def area(self) -> float:
        return pi * self.radius**2


if __name__ == "__main__":
    c = Circle(center=(1, 1), radius=2)
    print(c.model_dump())
    print(c.area)
