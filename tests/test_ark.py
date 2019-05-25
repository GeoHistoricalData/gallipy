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
import pytest
from gallipy.monadic import Right, Left
from gallipy import Ark

TEST_CASES = [
    ({"naan":"naan", "name":"name", "authority":"authority"}, ValueError),
    ({"scheme":"scheme", "authority":"authority"}, ValueError),
]

@pytest.mark.parametrize("test,expected", TEST_CASES)
def test_constructor_fails(test, expected):
    """Test constructor failures."""
    with pytest.raises(expected):
        Ark(**test)

TEST_CASES = [
    ({"naan":"n", "name":"n", "scheme":"s", "qualifier":"q"}),
    ({"scheme":"s", "authority":"a", "naan":"n", "name":"n", "qualifier":"q"}),
]
@pytest.mark.parametrize("test", TEST_CASES)
def test_constructor_succeeds(test):
    """Test constructor success."""
    Ark(**test)


TEST_CASES = [
    (None, Left),
    ('', Left),
    ('gallica.bnf.fr/ark:/12148/bpt6k5619759j', Left),  # Scheme is missing
    ('http:///ark:/12148/bpt6k5619759j', Left),  # NMAH is missing
    ('http://gallica.bnf.fr/', Left),  # ARKId is missing
    ('You can\'t see me', Left),  # JOHN CENA!
    ('12148/bpt6k5619759j', Left),  # Scheme is missing
    ('ark://12148', Left),  # Naan is missing
    ('ark:/12148/', Left),  # Name is missing + slash
    ('/ark:/12148/bpt6k5619759j', Left),  # Leading slash
    ('ark:/12148/bpt6k5619759j/', Left),  # Trailing slash
    ('ark:/12148/bpt6k?@:5619759j', Left),  # Invalid chars
    ('ark:/12148/bpt6k5619759j?date=1937', Left),  # Invalid ending
    ('ark:/12148/bpt6k5619759j#date', Left), # Qualifier must start with /
    ('ark:/12148/bpt6k5619759j', Right),  # Valid ARK id
    ('ark:/12148/bpt6k5619759j/f1n10.pdf', Right),  # Valid ARK id with qualifier
    ('https://gallica.bnf.fr/ark:/12148/bpt6k5619759j', Right), # Valid ARK
    ('https://gallica.bnf.fr/ark:/12148/bpt6k5619759j/f1n10.pdf', Right),
    ('https://gallica.bnf.fr/ark:/12148/bpt6k5619759j?date=date', Right), # Ark with additional infos
    ('https://gallica.bnf.fr/ark:/12148/bpt6k5619759j#date', Right), # Ark with additional infos
    ('https://gallica.bnf.fr/ark:/12148/bpt6k5619759j/f1n10.pdf?query=test', Right),
    ('https://gallica.bnf.fr/ark:/12148/bpt6k5619759j/f1n10.pdf#test', Right),
]

@pytest.mark.parametrize("test,expected", TEST_CASES)
def test_parser_behavior(test, expected):
    """Test ARK parsing."""
    assert isinstance(Ark.parse(test), expected)

TEST_CASES = [
    ('ark:/12148/bpt6k5619759j'),  # Valid ARK id
    ('ark:/12148/bpt6k5619759j/f1n10.pdf'),  # Valid ARK id with qualifier
    ('https://gallica.bnf.fr/ark:/12148/bpt6k5619759j'), # Valid ARK
    ('https://gallica.bnf.fr/ark:/12148/bpt6k5619759j/f1n10.pdf'),
]

@pytest.mark.parametrize("test", TEST_CASES)
def test_parser_output_equivalent_to_input_if_no_additional_info(test):
    """Test if result of parsing is equals to the input str"""
    assert Ark.parse(test).map(str).value == test

TEST_CASES = [
    ('ark:/12148/bpt6k5619759j', 'ark:/12148/bpt6k5619759j'),
    ('https://gallica.bnf.fr/ark:/12148/bpt6k5619759j?date=date', 'https://gallica.bnf.fr/ark:/12148/bpt6k5619759j'),
    ('https://gallica.bnf.fr/ark:/12148/bpt6k5619759j#date', 'https://gallica.bnf.fr/ark:/12148/bpt6k5619759j'),
    ('https://gallica.bnf.fr/ark:/12148/bpt6k5619759j/f1n1?date=date', 'https://gallica.bnf.fr/ark:/12148/bpt6k5619759j/f1n1'),
    ('https://gallica.bnf.fr/ark:/12148/bpt6k5619759j/f1n1.x_x.pdf#date', 'https://gallica.bnf.fr/ark:/12148/bpt6k5619759j/f1n1.x_x.pdf'),
]

@pytest.mark.parametrize("test,expected", TEST_CASES)
def test_additional_infos_ignored(test, expected):
    """Ensure that additional infos at the end on an ARK URL is ignored."""
    assert Ark.parse(test).map(str).value == expected

TEST_CASES = [
    ('https://gallica.bnf.fr/ark:/12148/bpt6k5619759j', 'ark:/12148/bpt6k5619759j'),
    ('https://gallica.bnf.fr/ark:/12148/bpt6k5619759j?date=date', 'ark:/12148/bpt6k5619759j'),
    ('ark:/12148/bpt6k5619759j', 'ark:/12148/bpt6k5619759j'),
    ('https://gallica.bnf.fr/ark:/12148/bpt6k5619759j#date', 'ark:/12148/bpt6k5619759j'),
]

@pytest.mark.parametrize("test,expected", TEST_CASES)
def test_extract_arkid_from_ark(test, expected):
    """Test ARK ID extraction from ARK URL."""
    assert Ark.parse(test).map(lambda x: x.arkid).map(str).value == expected

TEST_CASES = [
    ('ark:/12148/bpt6k5619759j/f1n10.pdf'),
    ('https://gallica.bnf.fr/ark:/12148/bpt6k5619759j'),
]

@pytest.mark.parametrize("test", TEST_CASES)
def test_copy(test):
    """Test copy constructor."""
    ark = Ark.parse(test).value
    assert str(ark.copy()) == str(ark)
