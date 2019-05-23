# Gallipy: yet another python wrapper for the Gallica APIs

Gallipy provides a simple access to gallica.bnf.fr [Document](http://api.bnf.fr/api-document-de-gallica) and [IIIF](http://api.bnf.fr/api-iiif-de-recuperation-des-images-de-gallica). The [Search API](http://api.bnf.fr/api-gallica-de-recherche) is not yet implemented. APIs are wrapped in a single class `Resource`, which is basically the 'R' in 'Archival Resouce Key'.

*Why a new package instead of forking Pyllica or PyGallica?*
I know, "thou should not reinvent the wheel"...but [you can't tell me what to do](https://www.youtube.com/watch?v=RYDy_nlgi5Q)!
Also I wanted to play with pythonic monades from [this **awesome** article](https://www.toptal.com/javascript/option-maybe-either-future-monads-js) by Alexey Karasev!

**Example**

Retrieve the first issue of the periodical journal *Le Journal de Toto* for the year 1937, then save this document as a PDF file.
```python
def retrieve_first_issue(issues):
  arkname = issues['issues']['issue'][0]['@ark']
  issue = Resource('ark:/12148/{}'.format(arkname))

  f = issue.content(mode='pdf') # Fetch the content of issue. f : Future[Either[Exception Binary]] 
  # If fetch wa successful, write the binary content to a file.
  bs_to_file = lambda bs : open('lejournaldetoto.pdf','wb').write(bs)
  f.map(lambda x : x.map(bs_to_file))

# Fetch the resource metadata with the service Issues and get the ARK id of the first issue in 1937
my_resource = Resource('https://gallica.bnf.fr/ark:/12148/cb32798952c/date')
issues = my_resource.issues(date=1937)  # issues: Future[Resource]
issues.map(retrieve_first_issue)  # retrieve_first_issue is the callback function
```

# Getting started

## Installation

`pip install gallipy`

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
my_resource.issues(date=1937)  # issues: Resource -> Future[Either[Exception Dict]]

# Synchronous call
my_resource.issues_sync(date=1937) # issues_sync: Resource -> Either[Exception Dict]
```
**Monadic objects**

All methods available from `Resource` return `Either` monadic objects for synchronous methods and `Future` objects for asynchronous ones.
I won't go into details about monades here because, honestly, I don't know much. Again, read [this](https://www.toptal.com/javascript/option-maybe-either-future-monads-js) for more details & explanations.

There's really ong things to know : any monade M[a] defines three functions
- `map: (a -> b) -> (M[a] -> M[b])` which takes a function that transform a to b promote it to a new function that apply to M[a] and returns M[b]
- `pure: a -> M[a]` which takes some a and wraps it
- `flat_map: (a -> M[b]) -> (M[a] -> M[b])` wich takes some function that takes an a and return a M[b] and makes it also work on M[a].

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
#### Issues
Retrieve metadata about a periodical journal. The optional parameter `date` will return metadata about all the issues that are available for a specific year.
```python
r = Resource('ark:/12148/cb32798952c/date')
# Resource -> Future[Either[Exception Dict]]
r.issues(date=1937)
# Resource -> Either[Exception Dict]
r.issues_sync()
```
#### OAIRecord
Retrieve the OAI record of a given document.
```python
r = Resource('ark:/12148/bpt6k5738219s')
# Resource -> Future[Either[Exception Dict]]
r.oairecord()
# Resource -> Either[Exception Dict]
r.oairecord_sync()
```

#### Pagination
Get paging informations about a document.
```python
r = Resource('ark:/12148/bpt6k5738219s')
# Resource -> Future[Either[Exception Dict]]
r.oairecord()
# Resource -> Either[Exception Dict]
r.oairecord_sync()
```

#### Table of content
Get the ToC of a document, in HTML.
```python
r = Resource('ark:/12148/bpt6k83037p/f143')
# Resource -> Future[Either[Exception HTMLString]]
r.toc()
# Resource -> Either[Exception HTMLString]
r.toc_sync()
```

#### Full-text search
Execute search queries on the text of a document. 
```python
r = Resource('ark:/12148/btv1b6930733g')
# Resource -> Future[Either[Exception Dict]]
r.fulltextsearch('hugo') # Search for 'hugo' in the whole document
# Resource -> Either[Exception Dict]
r.fulltextsearch_sync(query='hugo',page=10, startResult=1)  # Search for 'hugo' at page 10 and return all results in one 'page'.<
```

#### Content retrieve
Retrieve the content of a document. This is how you get the full PDFs.

Optional parameter `mode` can be 'pdf' or 'texteBrut' ('texteImage' is not supported). Default is 'pdf.'
```python
r = Resource('ark:/12148/btv1b693073')
# Resource -> Future[Either[Exception Binary]]
r.content() # Get all pages from r as a PDF

# Get pages 10 to 20 and save them as an html file.
e = r.content_sync(startPage=10, nPages=10, mode='textBrut')  
e.map(lambda x : open('myresource.html','wb').write(x))
```
The parameters `startPage` and `nPages` have precedence over the resource's ARK qualifier. Wich means that `Resource('ark:/12148/btv1b693073/f1n10.textBrut').content(startPage=10, nPages=10, mode=pdf)` will return pages 10 to 20 of resource `ark:/12148/btv1b693073` in PDF. `mode` will always be appended to the end of the qualifier.

### IIIF API

#### Document and image metadata
Retrieve metadata from an image or a whole document in JSON. 
```python
r = Resource('ark:/12148/btv1b90017179')

r.iiif_info(image='f15')  # Get metadata of page 15.
r.iiif_info_sync()  # Get metadata of the document  'ark:/12148/btv1b90017179'
```

#### Image retrieval
Retrieve an image using the IIIF API.

Parameters are detailed in http://api.bnf.fr/api-iiif-de-recuperation-des-images-de-gallica.
`region` is a 4-elements object of any iterable type.

The ARK qualifier has precedence over the parameter `image`, which means that `image` will be ignored if the resource's ARK is qualified.

```python
r = Resource('ark:/12148/btv1b90017179')

r.iiif_data(image='f15', imgtype='png')
e = r.iiif_data_sync(image='f15', region=(0, 0, 2400, 3898), imgtype='png')
```

#### Usage

Let's retrieve the first image of a document in native resolution
```python
ark = Ark.parse('https://gallica.bnf.fr/ark:/12148/btv1b90017179').value
r = Resource(ark)

metadata = r.iiif_info_sync().value
width = metadata['sequences'][0]['canvases'][0]['width']
height = metadata['sequences'][0]['canvases'][0]['height']

with open(ark.name+'_f1.png','bw') as o:
  o.write(r.iiif_data_sync(image='f1',fileformat='png', region=(0,0,width, height)).value)
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
- Implement the OCR retrieval.
- Provide an object representation of API response rather than  `OrderedDict`