from abc import ABCMeta, abstractmethod, abstractproperty


class Movable:
    __metaclass__ = ABCMeta

    @abstractmethod
    def move(self):
        """Переместить объект"""

    @abstractproperty
    def speed(self):
        """Скорость объекта"""