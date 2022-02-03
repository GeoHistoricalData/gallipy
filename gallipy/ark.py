from dataclasses import asdict, dataclass, fields
from lark import Transformer, Lark
from lark.exceptions import ParseError, UnexpectedCharacters


class ArkTransformer(Transformer):
    def _last(self, tokens):
        return tokens[-1].value

    def scheme(self, tokens) -> tuple:
        return "scheme", self._last(tokens)

    def authority(self, tokens) -> tuple:
        return "authority", self._last(tokens)

    def naan(self, tokens) -> tuple:
        return "naan", self._last(tokens)

    def name(self, tokens) -> tuple:
        return "name", self._last(tokens)

    def qualifier(self, tokens) -> tuple:
        return "qualifier", self._last(tokens)

    def ark(self, tokens) -> dict:
        print(tokens)
        return dict(t for t in tokens if t)


@dataclass(frozen=True)
class Ark:
    """
    Example of valid ARKs:
    - https://gallica.bnf.fr/ark:/12148/cb34431794k/date [ARK URL with qualifier]
    - ark:/12148/cb34431794k [long ARK ID]
    - 12148/cb34431794k [long ARK ID]
    - cb34431794k [short ARK ID]
    """

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
    _parser_transformer = ArkTransformer()

    scheme: str
    name: str  # name is mandatory
    authority: str
    naan: str
    qualifier: str

    def __init__(self, ark, **parts) -> None:
        fnames = [n.name for n in fields(self.__class__)]
        builder = dict.fromkeys(fnames)

        if isinstance(ark, Ark):
            builder.update(asdict(ark))

        elif isinstance(ark, str):
            parsed = self._parse_part(ark)
            builder.update(parsed)

        else:
            raise ValueError("Parameter ark must be an Ark object or a string")

        builder.update(parts)

        # Sanitize fields
        builder = {k: v or None for k, v in builder.items()}

        # Sanity checks before assignment
        assert all(
            [
                builder["name"],  # Name is mandatory
                all(" " not in v for v in filter(None, builder.values())),
            ]
        )

        if builder["authority"] and not builder["scheme"]:
            builder["scheme"] = "http"

        for name, value in builder.items():
            object.__setattr__(self, name, value)

    def __post_init__(self):
        # Verify one last time that the Ark is valid
        if not self.is_valid():
            raise ValueError(self)

    def short(self) -> str:
        """ Returns the short version of this Ark"""
        return self.__class__(self.name)

    def arkid(self):
        parts = asdict(self)
        parts = {k: v for k, v in parts.items() if k in ["naan", "qualifier"]}
        return self.__class__(self.name, **parts)

    def is_url(self) -> bool:
        """True if fields <authority> is set"""
        return self.authority

    def is_arkid(self) -> bool:
        """True if fields <naan> and <name> are set, but this ARK is not an URL."""
        return self.naan and not self.is_url()

    def is_short(self) -> bool:
        """True is only field <name> is set."""
        return not (self.naan or self.is_url())

    def is_valid(self) -> bool:
        """An Ark is valid if it matches the accepted parsed formats."""
        try:
            ark_str = repr(self)
            return bool(self._parse_part(ark_str))
        except ParseError:
            return False

    def __repr__(self) -> str:
        fields = [self.authority, self.naan, self.name, self.qualifier]

        if self.naan:
            fields[1] = "ark:/%s" % self.naan

        if self.is_url():
            fields.insert(0, "%s:/" % self.scheme)

        return "/".join(filter(None, fields))

    @classmethod
    def _parse_part(cls, ark_string):
        # try:
        tree = cls._parser.parse(ark_string)
        # except (ParseError, UnexpectedCharacters) as err:
        # raise ParseError("...") from err
        return cls._parser_transformer.transform(tree)


if __name__ == "__main__":
    ark_str = "ark:/12148/cb34431794k/date"
    ark = Ark.parse(ark_str)
    assert str(ark) == ark_str
    assert ark.is_arkid()
    assert not ark.is_short()
    assert not ark.is_arkurl()
    assert str(ark.short()) == "cb34431794k"
    print(ark)
