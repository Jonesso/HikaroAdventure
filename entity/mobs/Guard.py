from entity.Person import Person
from entity.interface.Movable import Movable


class Guard(Movable, Person):
    def __init__(self):
        super().__init__()
        self.c = None
        self.speed = 10
        self.x = 0

    @property
    def move(self):
        self.c += self.speed

    def speed(self):
        return self.speed
