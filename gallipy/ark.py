from typing import Optional, Union
from pydantic import validator
from pydantic import BaseModel
from lark import Token, Transformer, Lark


class ArkTransformer(Transformer):
    def scheme(self, tokens) -> tuple:
        return "scheme", self._value(tokens)

    def nma(self, tokens: Token) -> tuple:
        return "nma", "/".join([t.value for t in tokens if t])

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
    ark: [[scheme ":" _SEP~2] nma] ["ark"i ":" _SEP] naan _SEP name [_SEP qualifier]*
    scheme: /https?/
    nma: [PART _SEP]+
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


class Ark(BaseModel, frozen=False):

    # Permalink elements
    scheme: str = "http"
    nma: Optional[str]

    # Ark identifier
    naan: str
    name: str
    qualifiers: Union[str, list[str]] = []

    _parser: ArkParser = ArkParser()

    @validator("qualifiers")
    def qualifiers_to_list(cls, qualifiers):
        return qualifiers if isinstance(qualifiers, list) else [qualifiers]

    @classmethod
    def from_string(cls, ark_string: str) -> "Ark":
        sanitized_arkstring = ark_string.strip().lower()
        return cls._parser.parse(sanitized_arkstring)

    def identifier(self, with_qualifiers=True) -> str:
        parts = ["ark:", self.naan, self.name]
        if with_qualifiers:
            parts += self.qualifiers
        return "/".join(parts)

    def permalink(self, with_qualifiers=True) -> str:
        host = f"{self.scheme}://{self.nma}"
        identifier = self.identifier(with_qualifiers)
        return f"{host}/{identifier}"

    def __str__(self) -> str:
        return self.identifier()
