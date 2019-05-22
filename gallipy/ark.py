from rfc3987 import parse as rfcparse
from lark import Transformer, Lark
from lark.exceptions import ParseError, UnexpectedCharacters
from .monadic import Either, Left
import traceback

__all__ = ['Ark', 'ArkParsingError']

# ARKID structure :  ark:/NAAN/Name[Qualifier]
_GRAMMAR = """
    arkid: _ark_items _COLON _SLASH naan _SLASH name [ _SLASH qualifier ]
    naan: STRING
    name: STRING
    qualifier: STRING
    _SLASH: "/"
    _COLON: ":"
    _ark_items: "ark"i
    STRING: /[^:\/\?#\[\]@]+/
"""


class Ark:

    _fields = ["scheme", "authority", "naan", "name", "qualifier"]
    _arkidfields = ["scheme", "naan", "name", "qualifier"]

    def __init__(self, **arkinfo):
        # If authority is set then scheme must be set
        if arkinfo.get("authority") and not arkinfo.get("scheme"):
            msg = "Field 'scheme' and 'authority' \
            must be both set if one of them is set."
            raise ValueError(msg)
        # naan and name are required
        if not(arkinfo.get("naan") and arkinfo.get("name")):
            msg = "'naan' and 'name' are required fields."
            raise ValueError(msg)
        self._ark_items = {key: arkinfo.get(key) for key in self._fields}
    
    def copy():
        return Ark(self._ark_items)

    @property
    def scheme(self):
        return self._ark_items.get("scheme")

    @property
    def authority(self):
        return self._ark_items.get("authority")

    @property
    def naan(self):
        return self._ark_items.get("naan")

    @property
    def name(self):
        return self._ark_items.get("name")

    @property
    def qualifier(self):
        return self._ark_items.get("qualifier")

    @property
    def arkid(self):
        if self._ark_items.get('scheme') == 'ark':
            return self
        else:
            infos = self._ark_items.copy()
            # Change the scheme from whatever (e.g. http) to ark
            infos['scheme'] = 'ark' 
            items = {key: infos.get(key) for key in self._arkidfields}
            return Ark(**items)

    @staticmethod
    def parse(arkstr):
        try:
            arkdict = rfcparse(arkstr, rule="URI")  # Ensure ark is a URI
            arkid_parser = Lark(_GRAMMAR, start='arkid')
            if arkdict["scheme"] != 'ark':
                # If ArkID is nested inside an URL, extract it
                arkid = arkdict["path"].lstrip("/")
                if not arkdict["authority"]:  # The NMAH is required
                    msg = 'Name mapping authority cannot be null.'
                    raise ArkParsingError(msg, arkstr)
            else:
                arkid = arkstr
            tree = arkid_parser.parse(arkid)
            arkiddict = ArkIdTransformer().transform(tree)
            final_dict = {**arkdict, **arkiddict}
            return Either.pure(Ark(**final_dict))
        except (ParseError, UnexpectedCharacters) as e:
            return Left(ArkParsingError(str(e), arkstr))
        except Exception as e:
            return Left(e)

    def _str_ark_itemsid(self, arkiddict):
        pattern = "{scheme}:/{naan}/{name}"
        if arkiddict.get("qualifier"):
            pattern += "/{qualifier}"
        return pattern.format(**arkiddict)

    def _str_ark_itemsurl(self, arkurldict):
        return "{scheme}://{authority}/{arkid}".format(**arkurldict)

    def __str__(self):
        ark = self._str_ark_itemsid(self._ark_items)
        if self._ark_items.get("authority"):
            ark = self._str_ark_itemsurl({**self._ark_items, **{"arkid": ark}})
        return ark

    def __repr__(self):
        return str(self._ark_items)


class ArkParsingError(ValueError):

    def __init__(self, message, arkstr):
        template = """
            Parsing error, ARK '{}' is invalid. See details below.
            {}
        """
        super(ValueError, self).__init__(template.format(arkstr, message))


class ArkIdTransformer(Transformer):

    def naan(self, item):
        return "naan", str(item[-1])

    def name(self, item):
        return "name", str(item[-1])

    def qualifier(self, item):
        return "qualifier", str(item[-1])

    def arkid(self, items):
        return dict(items)
