import abc

class BotInterface:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def login(self):
        pass
        
    @abc.abstractmethod
    def find_car_number(self):
        pass
    
    @abc.abstractmethod
    def process(self):
        pass
        
    @staticmethod
    def  area_id():
        pass
    