from typing import Optional, Union
from pydantic import validator
from pydantic import BaseModel
from lark import Transformer, Lark


class ArkTransformer(Transformer):
    def scheme(self, tokens) -> tuple:
        return "scheme", self._value(tokens)

    def nma(self, tokens) -> tuple:
        return "nma", self._value(tokens)

    def naan(self, tokens) -> tuple:
        return "naan", self._value(tokens)

    def name(self, tokens) -> tuple:
        return "name", self._value(tokens)

    def qualifier(self, tokens) -> tuple:
        return "qualifier", self._value(tokens)

    def ark(self, tokens) -> dict:
        ark = {"qualifiers": []}
        for k, v in [t for t in tokens if t]:
            if k == "qualifier":
                ark["qualifiers"].append(v)
            else:
                ark[k] = v
        return ark

    def _value(a, tokens):
        return tokens[-1].value


class ArkParser:
    # Lark grammar of ARK identifiers
    GRAMMAR = """
    ark: [[scheme _SEP~2 ":"] nma _SEP] ["ark"i ":" _SEP] naan _SEP name [_SEP qualifier]*
    scheme: /https?/
    nma: PART
    naan: PART
    name: PART
    qualifier: PART
    PART: /[^@:\\/#\\[\\]\\?]+/i
    _SEP: "/"
    """

    _parser = Lark(GRAMMAR, start="ark")
    _transformer = ArkTransformer()

    @staticmethod
    def parse(ark_string):
        tree = ArkParser._parser.parse(ark_string)
        elements = ArkParser._transformer.transform(tree)
        return Ark(**elements)


class Ark(BaseModel, frozen=True):

    scheme: str = "http"
    nma: Optional[str]
    naan: str
    name: str
    qualifiers: Union[str, list[str]] = []

    _parser: ArkParser = ArkParser()

    @validator("qualifiers")
    def qualifiers_to_list(cls, qualifiers):
        print(qualifiers)
        return qualifiers if isinstance(qualifiers, list) else [qualifiers]

    @classmethod
    def from_string(cls, ark_string: str) -> "Ark":
        sanitized_arkstring = ark_string.strip().lower()
        return cls._parser.parse(sanitized_arkstring)

    def is_uri(self) -> bool:
        return self.nma is not None

    def short(self) -> str:
        parts = ["ark:", self.naan, self.name] + self.qualifiers
        return "/".join(parts)

    def __str__(self) -> str:
        ark = self.short()
        if self.is_uri():
            domain = f"{self.scheme}://{self.nma}"
            return f"{domain}/{ark}"
        return ark
