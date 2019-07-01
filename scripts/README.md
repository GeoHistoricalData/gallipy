A few scripts based on Gallipy
===

# getpdf.py: getting the PDF version of a resource hosted on Gallica from an ARK.

#### Examples
Download views 10 to 35 from the resource `https://gallica.bnf.fr/ark:/12148/bpt6k9764647w ` and save it as `bpt6k9764647w.pdf`.
```bash
./getpdf.py https://gallica.bnf.fr/ark:/12148/bpt6k9764647w bpt6k9764647w.pdf --start 10 --end 35
```
Download the entire resource `https://gallica.bnf.fr/ark:/12148/bpt6k9764647w `. As downloading large resources tends to fail due to timeout from Gallica, get this resource in blocks of 150 views.

```bash
./getpdf.py https://gallica.bnf.fr/ark:/12148/bpt6k9764647w bpt6k9764647w.pdf --start 10 --end 35 --blocksize 150
```

#### Usage
```bash
usage: getpdf.py [-h] [-s START] [-e END] [--blocksize BLOCKSIZE]
                 ark outputfile

A simple script to download the PDF version of an archival resource hosted by
Gallica.

positional arguments:
  ark                   The Archival Resource Key of the resource to download.
                        Can be a Gallica URL
                        (https://gallica.bnf.fr/ark:/12148/bpt6k9764647w) or
                        an ARK URI (ark:/12148/bpt6k9764647w)
  outputfile            The output PDF file.

optional arguments:
  -h, --help            show this help message and exit
  -s START, --start START
                        Index of the first view to download (starts at 1).
                        Default value: 1.
  -e END, --end END     Index of the last view to download. Default value: the
                        total number of views of this resource.
  --blocksize BLOCKSIZE
                        If defined, the resource will be downloaded in blocks
                        of --blocksize views. Default value: 300

```

# getpdfbib.py: getting the PDF version of a resource hosted on Gallica from Bibtex entries.
TODO