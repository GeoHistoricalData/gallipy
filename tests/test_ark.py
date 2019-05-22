import pytest
from gallipy.monadic import Right, Left
from gallipy import Ark

# ---
# ARK Parser 
# ---

ark_test_cases = [
  (None, Left),
  ('', Left),
  ('gallica.bnf.fr/ark:/12148/bpt6k5619759j', Left),  # Scheme is missing
  ('http:///ark:/12148/bpt6k5619759j', Left),  # NMAH is missing
  ('http://gallica.bnf.fr/', Left),  # ARKId is missing
  ('You can\'t see me', Left),  # JOHN CENA!
  ('https://gallica.bnf.fr/ark:/12148/bpt6k5619759j', Right), # Valid ARK
  ('https://gallica.bnf.fr/ark:/12148/bpt6k5619759j/f1n10.pdf', Right)  # Valid ARK with qualifier
]

@pytest.mark.parametrize("arkstring,expected", ark_test_cases)
def test_ark(arkstring, expected):
  assert type(Ark.parse(arkstring)) == expected

def test_ark_extract_arkid():
  ark = 'https://gallica.bnf.fr/ark:/12148/bpt6k5619759j'
  arkid = 'ark:/12148/bpt6k5619759j'
  parsed = Ark.parse(ark)
  assert str(parsed.value.arkid) == arkid

arkid_test_cases = [
  (None, Left),
  ('', Left),
  ('12148/bpt6k5619759j', Left),  # Scheme is missing  
  ('ark://12148', Left),  # Naan is missing
  ('ark:/12148/', Left),  # Name is missing
  ('You can\'t see me', Left),  # JOHN CENA!
  ('/ark:/12148/bpt6k5619759j', Left),  # Leading slash
  ('ark:/12148/bpt6k5619759j/', Left),  # Trailing slash
  ('ark:/12148/bpt6k5619759j', Right),  # Valid ARK id
  ('ark:/12148/bpt6k5619759j/f1n10.pdf', Right)  # Valid ARK id with qualifier
]

@pytest.mark.parametrize("arkidstring,expected", arkid_test_cases)
def test_arkid(arkidstring, expected):
    assert type(Ark.parse(arkidstring)) == expected