from dataclasses import asdict
from . import fixtures
from bs4 import BeautifulSoup, BeautifulStoneSoup
from document import Document, Ark
from bs4.element import Tag


def test_constructor():
    Document(Ark.parse("ark:/12148/btv1b53095291n"))  # from ark
    Document("ark:/12148/btv1b53095291n")  # from string


def test_service_issues():
    doc = Document("ark:/12148/cb32707911p/date")

    # All years
    all_years = doc.issues()
    del all_years["_parser"]
    del all_years["metadata"]["compile_time"]
    assert all_years == fixtures.issues

    all_years = doc.issues(raw=True)
    assert isinstance(all_years, BeautifulSoup)

    # Single year
    issues_1902 = doc.issues(1902)
    del issues_1902["_parser"]
    del issues_1902["metadata"]["compile_time"]
    assert issues_1902 == fixtures.issues_1902

    issues_1902 = doc.issues(1902, raw=True)  # as an XML object
    assert isinstance(issues_1902, BeautifulSoup)


def test_service_oairecord():
    doc = Document("bpt6k5738219s")
    oai = doc.oairecord()
    del oai["metadata"]["ResultsGenerationSearchTime"]
    del oai["_parser"]
    notice = oai.pop("notice")  # Don't bother comparing the notice content in detail
    assert isinstance(notice, Tag)
    assert oai == fixtures.oairecord

    oai = doc.oairecord(raw=True)  # as an XML object
    assert isinstance(oai, BeautifulSoup)


def test_service_pagination():
    doc = Document("ark:/12148/btv1b53095291n")
    pagination = doc.pagination()
    assert pagination == fixtures.pagination

    pagination = doc.pagination(raw=True)  # as an XML object
    assert isinstance(pagination, BeautifulSoup)


def test_service_contentsearch():
    doc = Document("bpt6k55506153")
    contentsearch = doc.contentsearch(query="intimider", page=5, start_result=1)
    del contentsearch["metadata"]["ResultsGenerationSearchTime"]
    del contentsearch["metadata"]["searchTime"]
    del contentsearch["_parser"]
    assert contentsearch == fixtures.contentsearch_onepage

    contentsearch = doc.contentsearch(query="intimider")
    del contentsearch["metadata"]["ResultsGenerationSearchTime"]
    del contentsearch["metadata"]["searchTime"]
    del contentsearch["_parser"]
    assert contentsearch == fixtures.contentsearch_allpages


def test_service_toc():
    doc = Document("ark:/12148/bpt6k165680m")
    assert str(doc.toc()) == fixtures.toc


def test_service_textebrut():
    doc = Document("ark:/12148/bpt6k62171919/f1")
    txt = doc.textebrut()
    assert isinstance(txt, BeautifulSoup)


def test_service_requestdigitalelement():
    doc = Document("bpt6k5619759j")
    de = doc.requestdigitalelement(3)
    assert isinstance(de, BeautifulSoup)
