import abc


class Base(metaclass=abc.ABCMeta):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def avaliar(self, texto, atendimentos):
        return

    @property
    def arquivo(self):
        return
