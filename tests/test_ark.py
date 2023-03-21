import dataclasses
from pydantic import ValidationError
import pytest
from lark.exceptions import ParseError, LexError
from ark import Ark


def test_minimalistic_ark_has_name():
    with pytest.raises(ValidationError):
        Ark()


# ----------------------------
# PARSING


@pytest.mark.parametrize(
    "invalid_ark_string",
    [
        "",  # Empty string
        "2148/btv1b8449691v/",  # Leading and trailing slashes #1
        "/2148/btv1b8449691v",  # Leading and trailing slashes #2
    ],
)
def test_invalid_parsing(invalid_ark_string: str):
    with pytest.raises((ParseError, LexError)):
        Ark.from_string(invalid_ark_string)


@pytest.mark.parametrize(
    "ark_string", ["http://example.org/ark:/13030/654xz321/s3/f8.05v.tiff",
                   "http://www.catalogue.fr/ark:/123/456",
                   "http://www.biblio-pour-internautes.fr/ark:/123/456",
                   "http://collections.banq.qc.ca/ark:/52327/61248"]
)
def test_parsing_complex_arks(ark_string):
    Ark.from_string(ark_string)


# def test_repr():
#     ark = Ark("name", naan="naan", qualifier="qualifier")
#     assert "ark:/naan/name/qualifier" == str(ark)


# def test_equality():
#     ark = Ark("name", naan="naan", qualifier="qualifier")
#     ark2 = Ark("name", naan="naan", qualifier="qualifier")
#     assert ark == ark2
#     assert Ark.parse("ark:/12148/cb32707911p/date") == Ark.parse(
#         "ark:/12148/cb32707911p/date"
#     )


# def test_only_name_is_mandatory():
#     Ark("name")
#     Ark.parse("name")


# def test_ark_is_immutable():
#     ark = Ark("name")
#     with pytest.raises(dataclasses.FrozenInstanceError):
#         ark.name = "something else"


# def test_copy_ark():
#     ark = Ark.parse("http://auth/ark:/naan/name/qualifier")
#     Ark(**dataclasses.asdict(ark))


# def test_parsed_ark_parts():
#     tests = [
#         "http://authority/ark:/naan/name/qualifier",
#         "ark:/naan/name/qualifier",
#         "naan/name/qualifier",
#         "naan/name",
#         "name",
#     ]
#     expected = [
#         Ark(
#             "name",
#             authority="authority",
#             httpscheme="http",
#             naan="naan",
#             qualifier="qualifier",
#         ),
#         Ark("name", naan="naan", qualifier="qualifier"),
#         Ark("name", naan="naan", qualifier="qualifier"),
#         Ark("name", naan="naan"),
#         Ark("name"),
#     ]
#     [Ark.parse(t) == exp for t, exp in zip(tests, expected)]


# def test_parse_invalid_arks():
#     with pytest.raises(ParseError):
#         Ark.parse("ark:/naan")  # Missing name #1
#     with pytest.raises(ParseError):
#         Ark.parse("authority/ark:/naan")  # Missing name #2
#     with pytest.raises(ParseError):
#         Ark.parse("/naan/name")  # Bad leading slash
#     with pytest.raises(ParseError):
#         Ark.parse("naan/name/")  # Bad trailing slash
#     with pytest.raises(ParseError):
#         Ark.parse("http://authority/naan/name/")  # `ark:` is missing


# def test_parse_unexpected_arks():
#     """Valid but unexpected parsing"""
#     ark = Ark.parse("name/qualifier")  # Parsed as naan/name
#     assert ark.naan == "name" and ark.name == "qualifier"
