from gallipy.ark import Ark
from gallipy.iiif import IIIF

def test_imagerequests():
    iiif = IIIF("ark:/12148/btv1b530532764")
    im = iiif.image_requests(1,(800,10000,2150,3000),(430,600),90,"native")
    assert im

def test_imageinformation():
    iiif = IIIF("ark:/12148/btv1b530532764")
    info = iiif.image_information(1)
    assert info and info["@id"] == "https://gallica.bnf.fr/iiif/ark:/12148/btv1b530532764/f1"

def test_presentation():
    iiif = IIIF("ark:/12148/btv1b530532764")
    pres = iiif.presentation()
    assert pres