# Gallipy: yet another Python wrapper for the Gallica APIs

Gallipy provides a pythonic way to access, query and retrieve (meta)data from gallica.bnf.fr, the digital library of the French National Library.
Gallipy wraps gallica's APIs [Document](http://api.bnf.fr/api-document-de-gallica) and [IIIF](http://api.bnf.fr/api-iiif-de-recuperation-des-images-de-gallica) in one single class named `Resource`, which basically which basically represents the 'R' in *Archival Resource Key*.

The [Search API](http://api.bnf.fr/api-gallica-de-recherche) is not yet implemented.

Gallipy implements pythonic Monades, as described in [this awesome article](https://www.toptal.com/javascript/option-maybe-either-future-monads-js) by Alexey Karasev. Monades Either/Maybe and Future are extensively used by gallipy.

**Example of use #1**

Download the first 10 views of the document with ark id `ark:/12148/btv1b90017179` in PDF format and save it on the disk.
```python
from gallipy import Resource, Ark

def save(either, filename):
  # Handle exceptions here
  if either.is_left:
    raise either.value
  # Otherwise we can safely unwrap its content.
  with open(filename,'wb') as file:
    file.write(either.value)
  return either  # Enables method chaining.

my_ark = 'ark:/12148/bpt6k5619759j'
filename = 'bpt6k5619759j.pdf'
# Async call: save(either, filename) is a callback method.
Resource(my_ark).content(startview=1, nviews=10, mode='pdf').map(lambda x: save(x, filename))
```

**Example of use #2**
Retrieve the first issue of the periodical journal *Le Journal de Toto* for the year 1937, then save this document as a PDF file.
```python
def retrieve_first_issue(issues):
  if issues.is_left:
    return issues
  arkname = issues.value['issues']['issue'][0]['@ark']
  issue_ark = Ark(naan='12148', name=arkname)
  issue = Resource(issue_ark)
  return issue.content_sync(mode='pdf')  # Sync call, get an Either

# Fetch the resource metadata with the service Issues and get the ARK id of the first issue in 1937
my_ark = 'https://gallica.bnf.fr/ark:/12148/cb32798952c'
filename = 'cb32798952c.pdf'
issues = Resource(my_ark).issues(year=1937)  # Async call
issues.map(retrieve_first_issue).map(lambda x: save(x, filename))
```

# Getting started

## Installation

`python setup.py install --user`

Gallipy requires **Python 3.5 or higher**. If you want to use it with Python 2.7.x, [do not hesitate to contribute](https://gist.github.com/Chaser324/ce0505fbed06b947d962) to this project.

## Overview
`Document` and `IIIF` are available from instance methods.
The constructor of `Resource` accepts Ark objects (see section "Parsing ARKs") or any valid ARK string of the form `[scheme://naming_authority/]ark:/name_assigning_authority_number/name[/qualifier]`.

Which means you can do things like:
```python 
from gallipy import Resource, Ark

# Full ARK string
my_resource = Resource('https://gallica.bnf.fr/ark:/12148/cb32798952c/date')

# ARK ID
my_other_resource = Resource('ark:/12148/btv1b6930733g/f1n200')

# Parse an ARK, build a Resource if the ARK is valid, otherwise return an Exception
ark = Ark.parse('https://gallica.bnf.fr/ark://12148/bpt6k5738219s')
my_third_resource = ark.map(Resource)
if my_third_resource.is_left:
  # Something went wrong
else:
  # Ready to query gallica.bnf.fr!
```

### Synchronous, asynchronous calls and monades
**Sync/async calls**

Gallipy allows for synchronous or asynchronous queries:
```python
# Asynchronous call
my_resource.issues(year=1937)  # Returns Future[Either[Exception Dict]]

# Synchronous call
my_resource.issues_sync(year=1937)  # Returns Either[Exception Dict]
```
**Monadic objects**

All methods available from `Resource` return `Either` monadic objects for synchronous methods and `Future` objects for asynchronous ones.
I won't go into details about monades here because, honestly, I don't know much. Again, read [this](https://www.toptal.com/javascript/option-maybe-either-future-monads-js) for more details & explanations.

**Either monade**

The Either monade is a very elegant way to deal with Exceptions. Either objects can be of two types: `Right[x]` if x is 'valid'(whatever it means)  and `Left[x]` otherwise. In Gallipy `Left` is only used to handle exceptions.

Here is an example with the Gallica service Pagination:
```python
r = Resource('ark:/12148/bpt6k5738219s')

# Resource -> Either[Exception Dict]
either = r.pagination_sync()

# ( Dict -> None ) -> (Either[Exception Dict] -> Either[Exception None] )
if either.map(print).is_left:
  raise either.value
```
Notice how this allows to deal with exceptions where you want, when you want : your program is safe as long as you don't unwrap the Either object.

**Future**

Futures are kinda similar to Javascript Promises. They let you execute a function asynchronously in a light, elegant way.
In Gallipy, all synchronous functions return some `x: Future[Either[...]]`:
```python
r = Resource('ark:/12148/bpt6kzzzzz5738219s')

def callback(either):
  # Unwrap either and print x: X its content if either: Right[X]
  # Otherwise either holds an exception, so we raise it.
  if e.map(print).is_left:
    raise e.value
  
r.pagination().map(callback)
```



### Document API
See the [official documentation](http://api.bnf.fr/api-document-de-gallica) for more details.
To get more information on a method, use `help(gallipy.some_method)` or you can read the sources as their contains docstrings for most API methods.
All methods are instance methods of the class `Resource`.

#### Issues
Retrieves metadata about a periodical journal. The optional parameter `year` will return metadata about all the issues that are available for a specific year.
```python
def issues(self, year=''):  # Async
def issues_sync(self, year=''):  # Sync
```
#### OAIRecord
Retrieve the OAI record of a given document.
```python
def oairecord(self):  # Async
def oairecord_sync(self):  # Sync
```

#### Pagination
Gets paging information about a document.
```python
def pagination(self):  # Async
def pagination_sync(self):  # Sync
```
#### Image Preview
Retrieves the preview image of a view in a resource.
```python
def image_preview(self, resolution='thumbnail', view=1):
def image_preview_sync(self, resolution='thumbnail', view=1):
```
#### Table of content
Get the ToC of a document, in HTML.
```python
def toc(self):
def toc_sync(self):
```
#### Full-text search
Executes search queries on the text of a document. 
```python
def fulltext_search(self, query='', view=1, results_per_set=10): 
def fulltext_search_sync(self, query, view=1, results_per_set=10):
```
#### Content retrieval
Retrieves the content of a document. This is how you get the full PDFs of any document.

Optional parameter `mode` can be 'pdf' or 'texteBrut' ('texteImage' is not supported). Default is 'pdf.'
```python
def content(self, startview=None, nviews=None, mode='pdf'):
def content_sync(self, startview=None, nviews=None, mode='pdf'):
```

#### OCR data
Retrieves the OCR data from a OCRized document.
```python
def ocr_data(self, view):
def ocr_data_sync(self, view):
```
### IIIF API
#### Document and image metadata
Retrieves metadata from an image or a whole document in JSON. 
```python
def iiif_info(self, view=''):
def iiif_info_sync(self, view=1):
```

#### Image retrieval
Retrieve an image using the IIIF API.

Parameters are detailed in http://api.bnf.fr/api-iiif-de-recuperation-des-images-de-gallica.
`region` is a 4-elements object of any iterable type.

```python
def iiif_data(self, view='', region=None, size='full', rotation=0, quality='native', imformat='png'):
    def iiif_data_sync(self, view=1, region=None, size='full', rotation=0, quality='native', imformat='png'):
```

## Parsing ARKs

Gallipy provides a parser for ARK urls and ARK ids.
The parser uses `rfc` for the optional non-id part of an ARK and Lark for the actual ARK id.

Buitl-in methods `__repr__` and `__str__` come in handy to handle ARK in a smooth way : 
```python
ark = Ark.parse('https://gallica.bnf.fr/ark:/12148/cb32798952c/date') # Parse the ark

ark.map(print)
# > https://gallica.bnf.fr/ark:/12148/cb32798952c/date

ark.map(lambda x : print(repr(x)))
# > {'scheme': 'https', 'authority': 'gallica.bnf.fr', 'naan': '12148', 'name': 'cb32798952c', 'qualifier': 'date'}

ark.map(lambda x : print(x.arkid))
# > ark:/12148/cb32798952c/date

ark.map(lambda x : print(repr(x.arkid)))
# > {'scheme': 'ark', 'authority': None, 'naan': '12148', 'name': 'cb32798952c', 'qualifier': 'date'}
```

# Todo
- Implement the Search API.
- Provide an better representation of API response than a simple  `OrderedDict`.