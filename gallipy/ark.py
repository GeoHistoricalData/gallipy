from dataclasses import asdict, dataclass
from collections import defaultdict
from lark import Transformer, Lark
from lark.exceptions import ParseError,UnexpectedCharacters

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

 
@dataclass(frozen=True)
class Ark:
    """An ARK ID (long or short) or an ARK URL.
    To create an Ark object from its string representation, use `Ark.parse("...")`.
    
    Example of valid ARKs:
    - https://gallica.bnf.fr/ark:/12148/cb34431794k/date [ARK URL with qualifier]
    - ark:/12148/cb34431794k [long ARK ID]
    - 12148/cb34431794k [long ARK ID]
    - cb34431794k [short ARK ID]

    Raises:
        ParseError: If a 

    Returns:
        Ark: A new ARK object.
    """
    name: str # <name> is the only mandatory part of an ARK
    httpscheme: str=None
    authority: str=None
    naan: str=None
    qualifier: str=None
       
    __ebnf = """
    ark: [[[[httpscheme _COLON _SLASH _SLASH] authority _SLASH] _ARK_NAMESPACE _COLON _SLASH] naan _SLASH] name [_SLASH qualifier]
    authority: ARK_PART
    naan: ARK_PART
    name: ARK_PART
    qualifier: ARK_PART
    _SLASH: "/"
    _COLON: ":"
    _ARK_NAMESPACE: "ark"i
    httpscheme: HTTP_OR_HTTPS
    HTTP_OR_HTTPS: /http[s]?/i
    ARK_PART: /[^@:\\/#\\[\\]\\?]+/
    """
    __transformer = _ArkTransformer()
    __parser = Lark(__ebnf, start='ark')

    def short(self) -> str:
        """ Returns the short version of this Ark"""
        return Ark(self.name)

    def is_arkurl(self) -> bool:
        """Is this Ark of the form [scheme://]<authority>/ark:/... ?"""
        return bool(self.authority)

    def is_arkid(self) -> bool:
        """Is this Ark of the form [ark:/]<naan>/<name>[/qualifier] or <name> ?"""
        return not self.is_arkurl()

    def is_short(self) -> bool:
        """Does this Ark holds only a `name` ?"""
        return self.is_arkid() and not self.naan

    def is_valid(self) -> bool:
        """An Ark is valid if it matches the accepted parsed formats."""
        authority_must_with_naan = bool(self.authority) and not bool(self.naan)
        scheme_must_with_authority = bool(self.httpscheme) and not bool(self.authority)
        return authority_must_with_naan and scheme_must_with_authority
        
    def __repr__(self) -> str:
        """Display this Ark as a simple string"""
        if self.is_short():
            return self.name
        
        ark = f"ark:/{self.naan}/{self.name}"
        if self.qualifier:
            ark = f"{ark}/{self.qualifier}"
        
        if self.is_arkurl():
            scheme = f"{self.httpscheme}:/" if self.httpscheme else ""
            ark = f"{scheme}/{self.authority}/{ark}"
        
        return ark
 
    @classmethod
    def parse(cls, ark_str:str) -> "Ark":
        """Parse an Ark object from its string representation.

        Accepted formats are: 
        - ARK URL: [<http_scheme>://]<authority>/ark:/<naan>/<name>[/<qualifier>]
        - Long ARK ID: [ark:/]<naan>/<name>[/<qualifier>]
        - Short ARK ID: <name>

        Args:
            ark_str (str): The string representation of an ARK ID or URL.

        Returns:
            Ark: The Ark object parsed from `ark_str`.
            
        Raises:
            ParseError: If the ARK string cannot be parsed.
        """
        try:
            tree = cls.__parser.parse(ark_str)
        except (ParseError, UnexpectedCharacters) as err:
            message = f"Failed to parse `{ark_str}`."
            message += "\nAccepted formats are:"
            message += "\n- Full ARK URL -> http[s]://<authority>/<naan>/<name>[/<qualifier>]"
            message += "\n- Long ARK ID -> [ark:/]<naan>/<name>[/<qualifier>]"
            message += "\n- Short ARK ID -> <name>"
            message += f"\nDetails:\n {err}"
            raise ParseError(message) from err
        ark_dict = cls.__transformer.transform(tree)
        return cls(**ark_dict)

if __name__ == "__main__":
    ark_str = "ark:/12148/cb34431794k/date"
    ark = Ark.parse(ark_str)
    assert str(ark) == ark_str
    assert ark.is_arkid()
    assert not ark.is_short()
    assert not ark.is_arkurl()
    assert str(ark.short()) == "cb34431794k"
    print(ark)