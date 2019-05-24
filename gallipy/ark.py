"""
Gallipy - Python wrapper for the Gallica APIs
Copyright (C) 2019  Bertrand Dumenieu

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

https://github.com/GeoHistoricalData/gallipy
"""
import rfc3987
from lark import Transformer, Lark
from lark.exceptions import ParseError, UnexpectedCharacters
from .monadic import Either, Left

__all__ = ['Ark', 'ArkParsingError']

# ARKID structure :  ark:/NAAN/Name[Qualifier]
_GRAMMAR = """
    arkid: _SCHEME _COLON _SLASH naan _SLASH name [_SLASH qualifier]
    naan: SAFESTRING
    name: SAFESTRING
    qualifier: SAFESTRING
    _SLASH: "/"
    _COLON: ":"
    _SCHEME: "ark"i
    SAFESTRING: /[^@:\\/#\\[\\]\\?]+/
"""

_ARKID_SCHEME = "ark"


class Ark:
    """Object representation of an Archival Resource Key.

    An object representation of an Archival Resource Key, which can be
    either a full ARK URL or an ARK ID, following the structure
    [urlscheme://authority/]ark:/naan/name[/qualifier].

    Args:
        naan (str): Name Assigning Authority Number.
        name (str): ARK ID name.
        qualifier (:obj:`str`, optional): ARK qualifier.
        scheme (:obj:`str`, optional): The scheme of the ARK.
            Can be any http scheme, or 'ark'. Defaults to 'ark'.
        authority (:obj:`str`, optional): The naming authority, e.g. gallica.bnf.fr.
            If authority is set them scheme must be a http scheme.
    Attributes:
        ark_parts (dict): A dictionary of ark parts. Must contain at least keys
            'naan' and 'name'. If key 'authority' is set, key 'scheme' must be
            different from 'ark'.
    Raises:
        ValueError: If parameters naan or name are undefined, or if scheme='ark'
            and authority is set.
    """

    def __init__(self, **ark_parts):
        valid_keys = ["scheme", "authority", "naan", "name", "qualifier"]
        parts = {key: ark_parts.get(key) for key in valid_keys}
        # Scheme must be ark if authority is unset. 'ark' is also scheme's
        # default value.
        if not(parts["scheme"] and parts["authority"]):
            parts["scheme"] = 'ark'

        # naan and name are required
        if not parts["naan"]:
            raise ValueError("Parameter naan is required.")
        if not parts["name"]:
            raise ValueError("Parameter name is required.")
        # scheme cannot be 'ark' if authority is set
        if parts["authority"] and parts["scheme"] == _ARKID_SCHEME:
            msg = """
            Cannot create an Ark object with parts {}
            Scheme cannot be '{}' if authority is set.
            """.format(str(parts), _ARKID_SCHEME)
            raise ValueError(msg)

        self._ark_parts = parts

    def copy(self):
        """Copy constructor.

        Returns:
            Ark: A copy of self
        """
        return Ark(**self._ark_parts)

    @property
    def scheme(self):
        """The scheme of this Ark.

        Returns:
            str: The scheme of self.
        """
        return self._ark_parts.get("scheme")

    @property
    def authority(self):
        """The authority of this Ark.

        Returns:
            str: The authority of self.
        """
        return self._ark_parts.get("authority")

    @property
    def naan(self):
        """The naming authority assigning number of this Ark.

        Returns:
            str: The naming assigning number of self.
        """
        return self._ark_parts.get("naan")

    @property
    def name(self):
        """The name of this Ark.

        Returns:
            str: The name of self.
        """
        return self._ark_parts.get("name")

    @property
    def qualifier(self):
        """The qualifier of this Ark.

        Returns:
            str: The qualifier of self.
        """
        return self._ark_parts.get("qualifier")

    @property
    def arkid(self):
        """The ARK ID of this Ark.

        If this Ark is an URL, extract the ARK ID nester inside as a new Ark
        object. Otherwise, return self.

        Returns:
            Ark: If self is a full ARK URL, a new Ark object representing the
            ARK ID nested in self. Otherwise, return self.
        """
        if self.is_arkid():
            return self
        parts = self._ark_parts.copy()
        parts['scheme'] = 'ark'
        del parts['authority']
        return Ark(**parts)

    def is_arkid(self):
        """The ARK ID of this Ark.
        Returns:
            bool: True if self is an ARK ID, False if self is a full ARK URL.
        """
        return self.scheme == _ARKID_SCHEME

    @staticmethod
    def parse(ark_str):
        """Parse an ARK URL or an ARK ID string into an Ark oject
            Args:
                ark_str (str): The string to parse.

            Returns:
                Ark: The parsed ARK.
        """
        try:
            parts = rfc3987.parse(ark_str, rule="URI")  # Ensure ark is a URI
            parser = Lark(_GRAMMAR, start='arkid')

            # Extract an ARK ID from ark_str if ark_str is a full ARK URL.
            if parts["scheme"] != _ARKID_SCHEME:
                arkid_str = parts["path"].lstrip("/")
                if not parts["authority"]:  # NMA is required
                    msg = 'Name Mapping Authority cannot be null.'
                    raise ArkParsingError(msg, ark_str)
            else:
                arkid_str = ark_str

            tree = parser.parse(arkid_str)
            ark_parts = ArkIdTransformer().transform(tree)
            ark_parts.update(parts)
            ark = Ark(**ark_parts)
            return Either.pure(ark)

        except (TypeError, ValueError, ParseError, UnexpectedCharacters) as ex:
            print(str(ex))
            return Left(ArkParsingError(str(ex), ark_str))

    def __str__(self):
        """Simple string representation of this Ark"""

        pattern = "{scheme}://{authority}/" if not self.is_arkid() else ""
        pattern += _ARKID_SCHEME+":/{naan}/{name}"
        pattern += "/{qualifier}" if self.qualifier else ""
        return pattern.format(**self._ark_parts)

    def __repr__(self):
        """Simple string representation of the parts composing this Ark"""
        return str(self._ark_parts)


class ArkParsingError(ValueError):
    """A simple parsing exceptions for Arks."""
    def __init__(self, message, arkstr):
        string = """
            Parsing error, ARK '{}' is invalid. See details below.
            {}
        """.format(arkstr, message)
        super().__init__(string)


class ArkIdTransformer(Transformer):
    """A tree transformer for Ark parsing."""

    @staticmethod
    def naan(item):
        """Get naan item from the naan TreeNode."""
        return "naan", str(item[-1])

    @staticmethod
    def name(item):
        """Get name item from the naan TreeNode."""
        return "name", str(item[-1])

    @staticmethod
    def qualifier(item):
        """Get qualifier item from the naan TreeNode."""
        return "qualifier", str(item[-1])

    @staticmethod
    def arkid(items):
        """Get arkid item from the naan TreeNode."""
        return dict(items)
