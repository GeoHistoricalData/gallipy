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
def test_constructor_nok(test, expected):
    """Test constructor failures."""
    with pytest.raises(expected):
        Ark(**test)

TEST_CASES = [
    ({"naan":"n", "name":"n", "scheme":"s", "qualifier":"q"}),
    ({"scheme":"s", "authority":"a", "naan":"n", "name":"n", "qualifier":"q"}),
]
@pytest.mark.parametrize("test", TEST_CASES)
def test_constructor_ok(test):
    """Test constructor success."""
    print(Ark(**test))


TEST_CASES = [
    (None, Left),
    ('', Left),
    ('gallica.bnf.fr/ark:/12148/bpt6k5619759j', Left),  # Scheme is missing
    ('http:///ark:/12148/bpt6k5619759j', Left),  # NMAH is missing
    ('http://gallica.bnf.fr/', Left),  # ARKId is missing
    ('You can\'t see me', Left),  # JOHN CENA!
    ('https://gallica.bnf.fr/ark:/12148/bpt6k5619759j', Right), # Valid ARK
    ('https://gallica.bnf.fr/ark:/12148/bpt6k5619759j/f1n10.pdf', Right),
    ('12148/bpt6k5619759j', Left),  # Scheme is missing
    ('ark://12148', Left),  # Naan is missing
    ('ark:/12148/', Left),  # Name is missing + slash
    ('/ark:/12148/bpt6k5619759j', Left),  # Leading slash
    ('ark:/12148/bpt6k5619759j/', Left),  # Trailing slash
    ('ark:/12148/bpt6k5619759j', Right),  # Valid ARK id
    ('ark:/12148/bpt6k?@:5619759j', Left),  # Invalid chars
    ('ark:/12148/bpt6k5619759j/f1n10.pdf', Right),  # Valid ARK id with qualifier
]

@pytest.mark.parametrize("test,expected", TEST_CASES)
def test_ark(test, expected):
    """Test ARK parsing."""
    assert isinstance(Ark.parse(test), expected)

def test_ark_extract_arkid():
    """Test ARK ID extraction from ARK URL."""
    ark = 'https://gallica.bnf.fr/ark:/12148/bpt6k5619759j'
    arkid = 'ark:/12148/bpt6k5619759j'
    parsed = Ark.parse(ark)
    assert str(parsed.value.arkid) == arkid

TEST_CASES = [
    ('ark:/12148/bpt6k5619759j/f1n10.pdf'),  # Valid ARK id with qualifier
]

@pytest.mark.parametrize("test", TEST_CASES)
def test_copy(test):
    """Test copy constructor."""
    assert str(Ark.parse(test).value) == str(Ark.parse(test).value.copy())
