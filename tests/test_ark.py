import pytest
from gallipy.gallipy.ark import *

def test_empty_ark_is_invalid():
    with pytest.raises(TypeError):
        Ark()

def test_empty_parsed_is_invalid():
    with pytest.raises(TypeError):
        Ark.parse()

def test_only_name_is_mandatory():
    Ark("name")
    Ark.parse("name")

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
    Ark.parse("ark:/naan")
