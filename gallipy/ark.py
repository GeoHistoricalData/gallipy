from pydantic import validator
from pydantic import BaseModel
from lark import Transformer, Lark
from collections import defaultdict


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
    ark: [[[scheme _SEP~2] nma _SEP "ark"i _SEP] naan _SEP] name [_SEP qualifier]*
    scheme: /https?/
    nma: PART
    naan: PART
    name: PART
    qualifier: PART
    PART: /[^@:\\/#\\[\\]\\?]+/i
    _SEP: "/"
    %ignore ":"
    """

    _parser = Lark(GRAMMAR, start="ark")
    _transformer = ArkTransformer()

    @staticmethod
    def parse(ark_string):
        tree = ArkParser._parser.parse(ark_string)
        elements = ArkParser._transformer.transform(tree)
        print(elements)
        return Ark(**elements)


class Ark(BaseModel, frozen=True):

    nma: str = None
    naan: str = None
    name: str
    qualifiers: list[str] = []
    scheme: str = "http"

    _parser: ArkParser = ArkParser()

    @validator("name")
    def name_is_mandatory(cls, name):
        if not name:
            raise ValueError("The element `name` is mandatory")
        return name

    @classmethod
    def from_string(cls, ark_string: str) -> "Ark":
        sanitized_arkstring = ark_string.strip().lower()
        return cls._parser.parse(sanitized_arkstring)

    def is_uri(self):
        return self.nma is not None

    def __str__(self) -> str:
        ark = "ark:" + "/".join([self.naan, self.name] + self.qualifiers)
        if self.is_uri():
            domain = f"{self.scheme}://{self.nma}"
            return f"{domain}/{ark}"
        return ark


print(Ark.from_string("http://www.biblio-pour-internautes.fr/ark:/123/456"))
