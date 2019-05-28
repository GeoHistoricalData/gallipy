from xmltodict import parse as parsexmltodict
from . import helpers as h
from .monadic import Left, Future
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
      raise ValueError("ark must be of type Ark or str.")

  @property
  def ark(self):
    return self._ark
  
  @property
  def arkid(self):
    return self.ark.arkid

  # ---
  # ASYNCHRONOUS METHODS
  # ---

  def issues(self, date=''):
      """Fetches metadata about the issues of a periodical journal (Async version). 

      The Document API service Issues retrieves metadata about a periodical journal.
      If a year is provided, issues_sync fetches metadata about all the issues of
      this specific year.
      Qualifiers are ignored.

      Args:
          year (:obj:int, optional): The year for which to retrieve the issues metadata.

      Returns:
          Future: A Future object that will holds an Either object if it resolved.
              This Either will hold the fetched data (Right) or an Exception (Left).
              For more details, see Resource.issues_sync.
      """
      return Future.asyn(lambda: self.issues_sync(date))

  def oairecord(self):
      """Retrieves the OAI record of a document (Async version). 

      The Document API service OAIRecord retrieves the OAI record of a document.
      Qualifiers are ignored.

      Returns:
          Future: A Future object that will holds an Either object if it resolved.
              representation of the metadata.
              This Either will hold the fetched data (Right) or an Exception (Left).
              For more details, see Resource.oairecord_sync.
      """
      return Future.asyn(self.oairecord_sync)

  def pagination(self):
      """Fetches paging metadata of a resource (Async version).

      The Document API service Pagination retrieves metadata about the paging
      of a document.
      Qualifiers are ignored.

      Returns:
          Future: A Future object that will holds an Either object if it resolved.
              representation of the metadata.
              This Either will hold the fetched data (Right) or an Exception (Left).
              For more details, see Resource.pagination_sync.
      """
      return Future.asyn(self.pagination_sync)

  def image_preview(self, resolution='thumbnail'):
    """
    """
    return Future.asyn(self.image_preview_sync)

  def fulltext_search(self, query='', page=1, results_per_set=10):
    """
    """
    l = lambda: self.fulltext_search_sync(query, page, results_per_set)
    return Future.asyn(l)

  def toc(self):
    """
    """
    return Future.asyn(self.toc_sync)

  def content(self, startpage=None, npages=None, mode='pdf'):
    """
    """
    l = lambda: self.content_sync(startpage, npages, mode)
    return Future.asyn(l)

  def ocr_data(self, page):
    """
    """
    l = lambda: self.ocr_data_sync(page)
    return Future.asyn(l)

  def iiif_info(self, image=''):
    """
    """
    l = lambda: self.iiif_info_sync(image)
    return Future.asyn(l)

  def iiif_data(self, image='', region=None, size='full', rotation=0, quality='native', imformat='png'):
    """
    """
    l = lambda: self.iiif_data_sync(image, region, size, rotation, quality, imformat)
    return Future.asyn(l)

  # ---
  # SYNCHRONOUS METHODS
  # ---

  def oairecord_sync(self):
      """Retrieves the OAI record of a document (Sync version). 

      Wraps Document API service 'OAIRecord'.
      The Document API service OAIRecord retrieves the OAI record of a document.
      Qualifiers are ignored.

      Returns:
          Either[Exception OrderedDict]: A Right object containing an OrderedDict
              representation of the metadata in case of success.
              Otherwise, a Left object containing an Exception.
      """
      try:
          url_parts = {"query": {"ark": self.ark.name }}
          url = h.build_service_url(url_parts, service_name="OAIRecord")
          return h.fetch_xml_html(url).map(parsexmltodict)
      except Exception as ex:
          return Left(ex)

  def issues_sync(self, year=''):
      """Fetches metadata about the issues of a periodical journal (Sync version). 

      Wraps Document API service 'Issues'.
      The Document API service Issues retrieves metadata about a periodical journal.
      If a year is provided, issues_sync fetches a set of of Gallica
       assumes that the ark ends with qualifier /date. Qualifiers are ignored.
      
      Args:
          year (:obj:int, optional): The year for which to retrieve
              the issues metadata.
      
      Returns:
          Either[Exception OrderedDict]: If fetch is successful, a Right object
              containing an OrderedDict representation of the metadata.
              Otherwise, a Left object containing an Exception.
      """
      try:  # Try/catch because Ark(...) can throw an exception.
          parts = self.ark.arkid.parts
          parts['qualifier'] = 'date'  # Qualifier must be 'date'
          url_parts = {"query":{"ark":Ark(**parts), "date":year}}
          url = h.build_service_url(url_parts, service_name="Issues")
          return h.fetch_xml_html(url).map(parsexmltodict)
      except Exception as ex:
          return Left(ex)

  def pagination_sync(self):
      """Fetches paging metadata of a resource (Sync version).

      Wraps Document API service 'Pagination'.
      The Document API service Pagination retrieves metadata about the paging
      of a document.
      Qualifiers are ignored.

      Returns:
          Either[Exception OrderedDict]: If fetch is successful, a Right object
              containing an OrderedDict representation of the metadata.
              Otherwise, a Left object containing an Exception.
      """
      url_parts = {"query": {"ark": self.ark.name}}
      url = h.build_service_url(url_parts, service_name="Pagination")
      return h.fetch_xml_html(url).map(parsexmltodict)

  def image_preview_sync(self, resolution='thumbnail', page=1):
      """Retrieves the preview image of a page in a resource (Sync version).

      Wraps Document API method 'Image précalculée'.
      Retrieves the preview of a page in a resource.
      Qualifiers are ignored.

      Args:
          resolution (:obj:str, optional): One of 'thumbnail', 'lowres', 'medres', 'highres'.
              Defaults to 'thumbnail'. 
          age (:obj:int, optional): The page to get the preview from. Defaults to 1.

      Returns:
          Either[Exception, Unicode]: If successful, a Right object
              containing the data of the preview image in JPEG format.
              Otherwise, a Left object containing an Exception.
      """
      url = h.build_base_url({"path":'{}/f{}.{}'.format(self.ark.root, page, resolution)})
      return h.fetch(url)

  def fulltext_search_sync(self, query, results_per_set=10):
      """Performs a full-text search in a plain-text Resource (sync version).

      Wraps Document API service 'ContentSearch'.
      Performs a word ou phrase search in a Resource with plain text available,
      using the service SearchContent. Returns the set of results as an OrderedDict.
      
      Phrases must be double quoted, e.g '"candidat à la présidence"'.
      You can combine multiple queries with commas or spaces.
      
      Note that the service SearchContent seems buggy: combining a phrase with
      a single word will result in Gallica searching for each word in the phrase,
      even if it is correctly double-quoted.
      Qualifiers are ignored.

      Args:
          query (str): The words to search for in the text.
          page (:obj:int, optional): The page in wich to search. If unset, query is
              performed on all pages.
          results_per_set (:obj:int, optional): Organises the results in sets of size
              results_per_set (max 10). Equivalent to startResult in the Document API.
              Defaults to 10.

      Returns:
          Either[Exception, OrderedDict]: If successful, a Right object
              containing the set of results as an OrderedDict.
              Otherwise, a Left object containing an Exception.
      """
      urlparts = {"query": {"ark": self.ark.name, "query": query, "startResult": results_per_set}}
      url = h.build_service_url(urlparts, service_name="ContentSearch")
      return h.fetch_xml_html(url).map(parsexmltodict)

  def toc_sync(self):
      """Retrieves the table of content of a resource as a HTML document.

      Wraps Document API service 'Toc'.
      Qualifiers are ignored.

      Returns:
          Either: If successful, a Right object containing the HTML ToC.
              Otherwise, a Left object containing an Exception.
      """    
      urlparts = {"query": {"ark": self.ark.name}}
      url = h.build_service_url(urlparts, service_name="Toc")    
      return h.fetch_xml_html(url, 'html.parser')

  def content_sync(self, startpage=1, npages=None, mode='pdf'):
      """Retrieves the content of a document.

      Wraps Document API method 'Texte Brut' and 'PDF'.
      self.qualifier is ignored by content_sync.
      If npages is not defined, the wholed document is downloaded using
      metadata retrieved by pagination_sync. 
      Qualifiers are ignored.
      
      Args:
          startpage (:obj:int, optional): The starting page to retrieve. Default: 1
          npages (:obj:int, optional): The number of pages to retrieve. Default: 1
          mode (:obj:int, optional): One of {'pdf, 'texteBrut'}. Default: 1
      
      Returns:
          Either[Exception Unicode]: The Unicode data of the content.
              Otherwise, a Left object containing an Exception.
      """
      _npages = 1
      if not npages:
        either = self.pagination_sync()
        if not either.is_left:
            _npages = int(either.value.get('livre').get('structure').get('nbVueImages'))
      else:
        _npages = npages
      _npages = _npages-startpage+1
      pattern = '{}/f{}n{}.{}'
      arkstr =pattern.format(self.ark.root, startpage, _npages, mode)
      urlparts = {"path": arkstr}
      url = h.build_base_url(urlparts)
      return h.fetch(url) if mode =='pdf' else h.fetch_xml_html(url, 'html.parser')

  def ocr_data_sync(self, page):
      """Retrieves the OCR data from a ocrized document.
   
      The OCR data is retrienve in XML ALTO and transfomed into an OrderedDict.
      Qualifiers are ignored.

      Args:
          page (int): Page number from wich to retrieve the OCR data.

      Returns:
          Either[Exception OrderedDict]: an Either object containing the OCR data in XML ALTO. 
              Otherwise, a Left object containing an Exception.
      """
      query = {"O":self.ark.name, "E":"ALTO", "Deb":page }
      urlparts = {"path": 'RequestDigitalElement', "query":query }
      url = h.build_base_url(urlparts)
      return h.fetch(url)

  def iiif_info_sync(self, page=1):
    """Retrieve IIIF metadata of a resource.

    Qualifiers are ignored.
    """
    if page:
      path = '{}/{}/f{}/{}'.format('iiif', self.ark.root, page, 'info.json')
    else:
      # No image param : user wants the whole document infos
      path = '{}/{}/{}'.format('iiif', self.ark.root, 'manifest.json')
    url = h.build_base_url({"path":path})
    print(url)
    return h.fetch_json(url).map(dict)

  def iiif_data_sync(self, page=1, region=None, size='full', rotation=0, quality='native', imformat='png'):
    """Retrieve image data from a resource using the IIIF API.

    Qualifiers are ignored.

    Args:
        page (:obj:int, optional): Page number to retrieve as an image.
        region (:obj:tuple, optional): The rectangular region of the
            image to extract as any 4-int iterable object :
            (lower left pixel, lower left pixel, width, height).
            If no region is provided, iiif_info_sync will be called to determine
            the size of the image. The entire image will be retrieved.
            If metadata retrieval fails, a window of size 1px will be extacted.
        size (:obj:str, optional): The size of the image to retrieve. Defaults to 'full'.
        rotation (:obj:int, optional): Rotate the image by an angle in degrees.
            Values between [0,360]. Defaults to 0.
        quality (:obj:str, optional): The quality of the retrieved image. Defaults
            to 'native'.
        imformat (:obj:str, optional): The returned data will be encoded for this format.
            Possible values are 'png', 'tif', 'jpg' and 'gif'. Defaults to 'png'.

    Returns:
        Either[Exception Unicode]: an Either object holding the image data, or an Exception. 
    """
    # If no region is provided, get the image size using iiif_info_sync(page)
    if not region:
        info = self.iiif_info_sync(page)
        width = 1 if info.is_left else info.value['width']
        height = 1 if info.is_left else info.value['height']
        region = (0, 0, width, height)

    region_str = ','.join(map(str, region))
    pattern = "iiif/{}/f{}/{}/{}/{}/{}.{}"
    path = pattern.format(self.ark.root, page, region_str, size, rotation, quality, imformat)
    urlparts = {"path": path}  
    url = h.build_base_url(urlparts)
    return h.fetch(url)