from . import helpers as h
from .monadic import Left, Right, Future
from .ark import Ark

class Resource():

  def __init__(self, ark):
    if isinstance(ark, Ark):
      self._ark = ark
    elif isinstance(ark,str):
      either = Ark.parse(ark)
      if either.is_left:
        raise either.value
      self._ark = either.value
    else:
      raise ValueError("ark must be of type Ark or string")

  @property
  def ark(self):
    return self._ark.copy()
  
  @property
  def arkid(self):
    return self._ark.arkid.copy()

  # ---
  # ASYNCHRONOUS METHODS
  # ---

  def issues(self, date=''):
    """
      Gallica service Issues
      Retrieve metadata about the issues of a periodical document knowing its 
      ARK.
      See http://api.bnf.fr/api-document-de-gallica#chapitre2
      :param ark: an Ark object that holds information about an ARK URI.
      :type ark: Ark
      :param date: If the optional parameter date is set, issues() will
      retrieve metadata for each of the issue in the periodical document for 
      that year.
      :type date: int
      :return a Future of the issues metadata for ark.
      :rtype monadic.Future
    """   
    return Future.asyn(lambda: self.issues_sync(date).value)

  def oairecord(self):
    """
      Gallica service OAIRecord
      Retrieve the bibliographic metadata of a document knowing its ARK.
      See http://api.bnf.fr/api-document-de-gallica#chapitre3
      :param ark: an Ark object that holds information about an ARK URI.
      :type ark: Ark
      :return a Future of the OAI metadata for ark.
      :rtype monadic.Future
    """
    return Future.asyn(lambda: self.oairecord_sync().value)

  def pagination(self):
    """
      Gallica service Pagination
      Retrieve the paging metadata of a document knowing its ARK.
      See http://api.bnf.fr/api-document-de-gallica#chapitre4
      :param ark: an Ark object that holds information about an ARK URI.
      :type ark: Ark
      :return a Future of the pagination metadata for ark.
      :rtype monadic.Future
    """
    return Future.asyn(lambda: self.pagination_sync())

  def image_preview(self, resolution='thumbnail'):
    """
    """
    return Future.asyn(lambda: imagereview_sync())

  def fulltextsearch(self, query='', page='', startResult=''):
    """
    """
    return Future.asyn(lambda: contentsearch_sync(query, page, startResult))

  def toc(self):
    """
    """
    return Future.asyn(lambda: toc_sync())

  def content(self, startPage=None, nPages=None, mode='pdf'):
    """
    """
    return Future.asyn(lambda: contentsearch_sync(startPage, nPages, mode))

  def iiif_info(self, image=''):
    """
    """
    return Future.asyn(lambda: contentsearch_sync(image))

  def iiif_data(self, image='', region=(0,0,1,1), size='full', rotation=0, quality='native', imgtype='png'):
    """
    """
    return Future.asyn(lambda: contentsearch_sync(image, region, size, rotation, quality, imgtype))

  @staticmethod
  def search():
    """
    """
    return Future.asyn(search_sync)

  # ---
  # SYNCHRONOUS METHODS
  # ---

  def oairecord_sync(self):
    urlparts = {"query": {"ark": self._ark.name }}
    url = h.build_service_url(urlparts, service_name="OAIRecord")
    return h.fetch_xml(url).map(h.xmltodict)

  def issues_sync(self, date=''):
    urlparts = {"query": {"ark": self._ark.arkid, "date": date }}
    url = h.build_service_url(urlparts, service_name="Issues")
    return h.fetch_xml(url).map(h.xmltodict)

  def pagination_sync(self):
    urlparts = {"query": {"ark": self._ark.name}}
    url = h.build_service_url(urlparts, service_name="Pagination")
    return h.fetch_xml(url).map(h.xmltodict)

  def imagepreview_sync(self, resolution='thumbnail'):
    if self._ark.qualifier:
      url = h.build_base_url(ark=self._ark.arkid)
    else:
      url = h.build_base_url({"path" : str(self._ark.arkid) + '.'+resolution})
    return h.fetch(url)

  def fulltextsearch_sync(self, query='', page='', startResult=''):
    urlparts = {"query": {"ark": self._ark.name, "query": query, "startResult": startResult}}
    url = h.build_service_url(urlparts, service_name="ContentSearch")
    return h.fetch_xml(url).map(h.xmltodict)

  def toc_sync(self):
    urlparts = {"query": {"ark": self._ark.name}}
    url = h.build_service_url(urlparts, service_name="Toc")    
    return h.fetch_xml(url)

  def content_sync(self, startPage=None, nPages=None, mode=None):
    # startPage and nPages have precedence over self._ark.qualifier
    qualifier = 'f{}'.format(startPage) if startPage else None
    qualifier = '{}n{}'.format(qualifier, nPages) if nPages else None
    
    if qualifier:
      arkstr = 'ark:/{}/{}/{}'.format(self._ark.naan, self._ark.name,qualifier)
    else:
      arkstr = str(self._ark.arkid)
    arkstr = '{}.{}'.format(arkstr, mode)
    urlparts = {"path": arkstr}
    url = h.build_base_url(urlparts)
    print(url)
    return h.fetch(url)

  def iiif_info_sync(self, image=''):
    if self._ark.qualifier or image:
      path = '/'.join(map(str,['iiif', self._ark.arkid, image, 'infos.json']))
    else:
      # No qualifier nor image param : user wants the whole document infos
      path = '/'.join(map(str, ['iiif', self._ark.arkid,'manifest.json']))
    urlparts = {"path": path}  
    url = h.build_base_url(urlparts)
    return h.fetch_json(url).map(h.jsontodict)

  def iiif_data_sync(self, image='', region=(0,0,1,1), size='full', rotation=0, quality='native', imgtype='png'):
    region_str = ','.join(map(str, region))
    path = '/'.join(map(str,['iiif', self._ark.arkid]))
    # If this._ark has a qualifier then parameter image is ignored.
    if self._ark.qualifier:
      path = '/'.join(map(str,[path, region_str, size, rotation, quality]))
    else:
      path = '/'.join(map(str,[path, image, region_str, size, rotation, quality]))
    path += '.'+imgtype
    urlparts = {"path": path}  
    print(path)
    url = h.build_base_url(urlparts)
    print(url)
    return h.fetch(url)

    @staticmethod
    def search_sync():
      return Left('NOT YET IMPLEMENTED')