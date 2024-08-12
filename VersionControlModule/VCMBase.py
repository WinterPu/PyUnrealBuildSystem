from abc import ABC,abstractmethod
from enum import StrEnum

from Utility.HeaderBase import *

class VCMType(StrEnum):
    Git = "Git"
    SVN = "SVN"

class VCMBase(ABC):
    # ModuleName = ""
    # def __init__(self,ModuleName) -> None:
    #     self.ModuleName = ""
    @classmethod
    @abstractmethod
    def GetModuleName(self):
        pass
