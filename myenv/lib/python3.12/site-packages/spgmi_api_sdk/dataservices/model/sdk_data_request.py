from typing import List, Optional, Dict
from collections import OrderedDict

class SDKDataRequest:
    def __init__(self, function: str = None, properties: Optional[Dict[str, str]] = None, identifiers: Optional[List[str]] = None, mnemonics: Optional[List[str]] = None):
        self.function = function
        self.properties = properties or {}
        self.identifiers = self.remove_duplicates(identifiers or [])
        self.mnemonics = self.remove_duplicates(mnemonics or [])

    def get_function(self) -> str:
        return self.function

    def set_function(self, function: str) -> None:
        self.function = function

    def get_properties(self) -> Dict[str, str]:
        return self.properties

    def set_properties(self, properties: Dict[str, str]) -> None:
        self.properties = properties

    def get_identifiers(self) -> List[str]:
        return self.identifiers

    def set_identifiers(self, identifiers: List[str]) -> None:
        self.identifiers = self.remove_duplicates(identifiers)

    def get_mnemonics(self) -> List[str]:
        return self.mnemonics

    def set_mnemonics(self, mnemonics: List[str]) -> None:
        self.mnemonics = self.remove_duplicates(mnemonics)

    def remove_duplicates(self, elements: List[str]) -> List[str]:
        unique_elements_caps = [element.upper() for element in elements]
        unique_elements = list(OrderedDict.fromkeys(unique_elements_caps))
        return unique_elements

    def __str__(self) -> str:
        return f"Function: {self.function}, Properties: {self.properties}, Identifiers: {self.identifiers}, Mnemonics: {self.mnemonics}"
