import imghdr
import json
import pytest
from gallipy import Resource, Ark
from gallipy.monadic import Right, Left
from bs4 import BeautifulSoup

TEST_CASES = [
    ({"naan":"n", "name":"n", "scheme":"s", "qualifier":"q"}),
    ({"scheme":"s", "authority":"a", "naan":"n", "name":"n", "qualifier":"q"}),
]

@pytest.mark.parametrize("case", TEST_CASES)
def test_construct_from_Ark(case):
  """Test constructing a Resource from an Ark object."""
  Ark.parse(case).map(Resource)

TEST_CASES = [
    ("https://gallica.bnf.fr/ark:/12148/cb32798952c/date"),
    ("https://gallica.bnf.fr/ark:/12148/cb32798952c/date&date=1937"),
    ("ark:/12148/cb32798952c/date"),
    ("ark:/12148/cb32798952c/date&date=1937"),
    ("ark:/12148/cb32798952c/date&date=1937"),
]

@pytest.mark.parametrize("case", TEST_CASES)
def test_construct_from_str(case):
  """Test constructing a Resource from a str."""
  Resource(case)

TEST_CASES = [
    ("https://gallica.bnf.fr/ark:/12148/cb32798952c/date", {"year":1937}, Right),
    ("ark:/12148/cb32798952c/date", {"year":1937}, Right),
    ("ark:/12148/cb32798952c/date", {}, Right),
    ("https://gallica.bnf.fr/ark:/12148/cb32798952c/f1n1", {}, Right),
    ("ark:/12148/cb32798952c/f1n10.pdf", {}, Right),
    ("https://gallica.bnf.fr/ark:/12148/cb32798952c", {}, Right),
]

@pytest.mark.parametrize("case, params, expected", TEST_CASES)
def test_issues_sync_ok(case, params, expected):
  """Test service Issues"""
  issues = Resource(case).issues_sync(**params)
  assert isinstance(issues, expected)



# def test_oairecord_sync():
#   # OAIRecord
#   arkstring = 'https://gallica.bnf.fr/ark:/12148/bpt6k5738219s'
#   oairecord = Resource(arkstring).oairecord_sync()
#   Right(oairecord.value).map(printmejson)
#   assert not oairecord.is_left

# def test_pagination_sync():
#   # Pagination
#   arkstring = 'https://gallica.bnf.fr/ark:/12148/bpt6k5738219s'
#   pagination = Resource(arkstring).pagination_sync()
#   Right(pagination.value).map(printmejson)
#   assert not pagination.is_left

# def test_pagination_sync_qualifier():
#   # Pagination
#   arkstring = 'https://gallica.bnf.fr/ark:/12148/bpt6k5738219s/f1n1'
#   pagination = Resource(arkstring).pagination_sync()
#   Right(pagination.value).map(printmejson)
#   assert not pagination.is_left


# def test_imagepreview_sync_thumbnail():
#   # ImagePreview
#   arkstring = 'https://gallica.bnf.fr/ark:/12148/btv1b6930733g'
#   image = Resource(arkstring).imagepreview_sync(resolution='thumbnail')
#   Right(image.value).map(saveme)
#   assert not image.is_left

# def test_imagepreview_sync_lowres():
#   # ImagePreview
#   arkstring = 'https://gallica.bnf.fr/ark:/12148/btv1b6930733g'
#   image = Resource(arkstring).imagepreview_sync(resolution='lowres')
#   Right(image.value).map(saveme)
#   assert not image.is_left
  
# def test_imagepreview_sync_medres():
#   # ImagePreview
#   arkstring = 'https://gallica.bnf.fr/ark:/12148/btv1b6930733g'
#   image = Resource(arkstring).imagepreview_sync(resolution='medres')
#   #Right(image.value).map(saveme)
#   assert not image.is_left

# def test_imagepreview_sync_highres():
#   # ImagePreview
#   arkstring = 'https://gallica.bnf.fr/ark:/12148/btv1b6930733g'
#   image = Resource(arkstring).imagepreview_sync(resolution='medres')
#   #Right(image.value).map(saveme)
#   assert not image.is_left

# def fulltextsearch():
#   # Full-text search
#   arkstring = 'https://gallica.bnf.fr/ark:/12148/btv1b6930733g'
#   searchcontent = Resource(arkstring).contentsearch_sync(query='hugo')
#   assert not searchcontent.is_left
#   Right(searchcontent.value).map(printmejson)

# def test_toc_sync():
#   # Table of Content
#   arkstring = 'https://gallica.bnf.fr/ark:/12148/btv1b6930733g'
#   toc = Resource(arkstring).toc_sync()
#   assert not toc.is_left
#   Right(toc.value).map(lambda x: print(BeautifulSoup(x,"html.parser").prettify()))



printmejson = lambda content : print(content if isinstance(content, Exception) else json.dumps(content, indent=4, ensure_ascii=False))

saveme = lambda binary : open('imagePreview.'+imghdr.what('',h=binary),'wb').write(binary)
