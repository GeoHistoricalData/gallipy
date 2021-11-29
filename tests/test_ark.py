import dataclasses
import pytest
from lark.exceptions import ParseError
from ark import Ark

def test_empty_ark_is_invalid():
    with pytest.raises(TypeError):
        Ark()

def test_empty_parsed_is_invalid():
    with pytest.raises(TypeError):
        Ark.parse()

def test_repr():
    ark = Ark("name",naan="naan",qualifier="qualifier")
    assert "ark:/naan/name/qualifier" == str(ark)
    
def test_equality():
    ark = Ark("name", naan="naan", qualifier="qualifier")
    ark2 = Ark("name", naan="naan", qualifier="qualifier")
    assert ark == ark2
    assert Ark.parse("ark:/12148/cb32707911p/date") == Ark.parse("ark:/12148/cb32707911p/date")

def test_only_name_is_mandatory():
    Ark("name")
    Ark.parse("name")

def test_ark_is_immutable():
    ark = Ark("name")
    with pytest.raises(dataclasses.FrozenInstanceError):
        ark.name = "something else"

def test_copy_ark():
    ark = Ark.parse("http://auth/ark:/naan/name/qualifier")
    Ark(**dataclasses.asdict(ark))

def test_parsed_ark_parts():
    tests = [
        "http://authority/ark:/naan/name/qualifier",
        "ark:/naan/name/qualifier",
        "naan/name/qualifier",
        "naan/name",
        "name"
    ]
    expected = [
        Ark("name",authority="authority",httpscheme="http",naan="naan", qualifier="qualifier"),
        Ark("name",naan="naan", qualifier="qualifier"),
        Ark("name",naan="naan", qualifier="qualifier"),
        Ark("name",naan="naan"),
        Ark("name")
    ]
    [Ark.parse(t) == exp for t, exp in zip(tests, expected)]

def test_parse_invalid_arks():
    with pytest.raises(ParseError):
        Ark.parse("ark:/naan")  # Missing name #1
    with pytest.raises(ParseError):
        Ark.parse("authority/ark:/naan")  # Missing name #2
    with pytest.raises(ParseError):
        Ark.parse("/naan/name")  # Bad leading slash
    with pytest.raises(ParseError):
        Ark.parse("naan/name/")  # Bad trailing slash
    with pytest.raises(ParseError):
        Ark.parse("http://authority/naan/name/")  # `ark:` is missing

def test_parse_unexpected_arks():
    """Valid but unexpected parsing"""
    ark = Ark.parse("name/qualifier")  # Parsed as naan/name
    assert ark.naan == "name" and ark.name == "qualifier"
