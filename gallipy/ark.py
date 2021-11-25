from dataclasses import dataclass, asdict
from lark import Transformer, Lark
from lark.exceptions import ParseError
import functools

ARK_EBNF = """
    ark: [[[[httpscheme _COLON _SLASH _SLASH] authority _SLASH] _ARK _COLON _SLASH] naan _SLASH] name [_SLASH qualifier]
    authority: SAFESTRING
    naan: SAFESTRING
    name: SAFESTRING
    qualifier: SAFESTRING
    _SLASH: "/"
    _COLON: ":"
    _ARK: "ark"i
    httpscheme: HTTP
    HTTP: /http[s]?/i
    SAFESTRING: /[^@:\\/#\\[\\]\\?]+/
"""

class _ArkTransformer(Transformer):
    def httpscheme(self, tokens) -> tuple:
        return "httpscheme", tokens[-1].value

    def authority(self, tokens) -> tuple:
        return "authority", tokens[-1].value

    def naan(self, tokens) -> tuple:
        return "naan", tokens[-1].value
    
    def name(self, tokens) -> tuple:
        return "name", tokens[-1].value

    def qualifier(self, tokens) -> tuple:
        return "qualifier", tokens[-1].value
    
    def ark(self, tokens) -> dict:
        filtered = [t for t in tokens if t]
        return dict(filtered)

 
@dataclass(frozen=True, repr=False)
class Ark:
    name: str # Arks have always a name
    httpscheme: str=None
    authority: str=None
    naan: str=None
    qualifier: str=None
       
    __transformer = _ArkTransformer()
    __parser = Lark(ARK_EBNF, start='ark')
    
    def is_arkurl(self) -> bool:
        return bool(self.authority)

    def is_arkid(self) -> bool:
        return not self.is_arkurl() # bool(self.naan) and 

    def is_short(self) -> bool:
        return not self.naan

    def __repr__(self) -> str:
        repr  = f"{self.httpscheme}://{self.authority}/" if self.authority else ""
        repr += f"ark:/{self.naan}/{self.name}" if self.naan else self.name
        repr += f"/{self.qualifier}" if self.qualifier else ""
        return repr

    @classmethod
    def parse(cls, ark_str:str) -> "Ark":
        try:
            tree = cls.__parser.parse(ark_str)
        except ParseError as err:
            message = f"Failed to parse `{ark_str}`."
            message += "\nAccepted formats are:"
            message += "\n- Full ARK URL : http[s]://<authority>/<naan>/<name>[/<qualifier>]"
            message += "\n- Long ARK ID : [ark:/]<naan>/<name>[/<qualifier>]"
            message += "\n- Short ARK ID : <name>"
            message += f"\nDetails: {err}"
            raise ValueError(message) from err
        ark_dict = cls.__transformer.transform(tree)
        return cls(**ark_dict)

if __name__ == "__main__":
    ark_str = "ark:/12148/cb34431794k/date"
    ark = Ark.parse(ark_str)
    print(ark)
    assert str(ark) == ark_str
    print("is ARK URL ?", ark.is_arkurl())
    print("is ARK ID ?", ark.is_arkid())
    print("is short ARK ?", ark.is_short())
