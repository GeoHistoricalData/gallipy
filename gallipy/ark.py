from dataclasses import asdict, dataclass, fields
from lark import Transformer, Lark
from .helpers import drop_none
from lark.exceptions import ParseError, UnexpectedCharacters


class ArkTransformer(Transformer):
    def scheme(self, tokens) -> tuple: return "scheme", self._value(tokens)
    def authority(self, tokens) -> tuple: return "authority", self._value(tokens)
    def naan(self, tokens) -> tuple: return "naan", self._value(tokens)
    def name(self, tokens) -> tuple: return "name", self._value(tokens)
    def qualifier(self, tokens) -> tuple: return "qualifier", self._value(tokens)
    def ark(self, tokens) -> dict: return dict(t for t in tokens if t)
    def _value(tokens): return tokens[-1].value

@dataclass(frozen=True)
class Ark:
    """
    Example of valid ARKs:
    - https://gallica.bnf.fr/ark:/12148/cb34431794k/date [ARK URL with qualifier]
    - ark:/12148/cb34431794k [long ARK ID]
    - 12148/cb34431794k [long ARK ID]
    - cb34431794k [short ARK ID]
    """

    # ~~~
    # Fields
    scheme: str
    name: str # name is mandatory
    authority: str
    naan: str
    qualifier: str
    # ~~~

    # Extended Backus-Naur form of an Ark, used by the Lark parser 
    # to extract the Ark components from a string representation.
    EBNF = """
    ark: [[[[scheme _COLON _SLASH _SLASH] authority _SLASH] _ARK_NAMESPACE _COLON _SLASH] naan _SLASH] name [_SLASH qualifier]
    authority: ARK_PART
    naan: ARK_PART
    name: ARK_PART
    qualifier: ARK_PART
    _SLASH: "/"
    _COLON: ":"
    _ARK_NAMESPACE: "ark"i
    scheme: SCHEMERULE
    SCHEMERULE: /http[s]?/i
    ARK_PART: /[^@:\\/#\\[\\]\\?]+/
    """
    
    _parser = Lark(EBNF, start="ark")
    _transformer = ArkTransformer()


    def __init__(self, ark, default_scheme="http", **components) -> None:
        fields_names = [f.name for f in fields(type(self))]
        fields_dict = dict.fromkeys(fields_names)

        # An ark can be created in three ways:
        # - from its components passed separately in parameters
        # - from a string representation
        # - from an existing Ark object
        # In the last 2 cases, the components of the ark given in parameter
        #  can be rewritten partially or totally using keyword arguments.
        if isinstance(ark, Ark):
            fields_dict.update(asdict(ark))
        elif isinstance(ark, str):
            fields_dict.update(self._parse(ark))
        else:
            raise ValueError("`ark` must be provided either as an Ark object or a string.")

        # Fields values are replaced with the additional components 
        # passed to the constructor as keyword arguments
        fields_dict.update(components)

        # Dispose of empty field values
        fields_dict = {k: v or None for k, v in fields_dict.items()}

        # Sanity checks before assignment:
        # - Name is mandatory
        # - Whitespaces are not allowed
        assert all(
            [
                fields_dict["name"],
                all(" " not in v for v in drop_none(fields_dict.values())),
            ]
        )

        if fields_dict["authority"] and not fields_dict["scheme"]:
            fields_dict["scheme"] = default_scheme

        for name, value in fields_dict.items():
            object.__setattr__(self, name, value)

    def __post_init__(self):
        """Once all components have been set, verify that this Ark is valid 

        Raises:
            ValueError: if self is not a valid Ark as defined in Ark.is_valid()
        """
        if not self.is_valid():
            raise ValueError(self)

    def short(self) -> str:
        """Returns the short version of this Ark"""
        return type(self)(self.name)

    def arkid(self):
        """Returns the long version of this Ark.
        If this is a short Ark, will return the short representation anyway."""
        components = asdict(self)
        components = {k: v for k, v in components.items() if k in ["naan", "qualifier"]}
        return type(self)(self.name, **components)

    def is_url(self) -> bool:
        """Returns True if this Ark is a full URL, i.e. if the field `authority` is set."""
        return self.authority

    def is_arkid(self) -> bool:
        """Returns True if this ark is a long Ark but not an URL, i.e. if the fields `naan` is set but not `authority`."""
        return self.naan and not self.is_url()

    def is_short(self) -> bool:
        """Returns True if this ark is a short Ark, i.e. if there is no `naan`."""
        return not self.naan and not self.is_url()

    def is_valid(self) -> bool:
        """An Ark is valid if it matches one of the accepted parsed formats, i.e.: 
        - a short Ark: name[/qualifier]
        - a long Ark: [ark:/]naan/name[/qualifier]
        - a full URL: [scheme://]authority/ark:/naan/name[/qualifier]
        """
        try:
            return any(self._parse(repr(self)))
        except ParseError:
            return False

    def __repr__(self) -> str:
        fields = [self.authority, self.naan, self.name, self.qualifier]

        if self.naan:
            fields[1] = "ark:/%s" % self.naan

        if self.is_url():
            fields.insert(0, "%s:/" % self.scheme)

        return "/".join(drop_none(fields))

    @classmethod
    def _parse(cls, ark_string: str) -> dict[str]:
        """Parse an Ark represented as a string into a dictionary of components.

        Args:
            ark_string (str): the ark string to parse

        Returns:
            dict[str]: the dictionary of components extracted from the input ark string
        """
        tree = cls._parser.parse(ark_string)
        return cls._transformer.transform(tree)
