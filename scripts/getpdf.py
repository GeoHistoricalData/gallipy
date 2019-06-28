#!/usr/bin/env python3

from gallipy import Resource, Ark
from gallipy.monadic import Left
from PyPDF2 import PdfFileReader, PdfFileWriter
import io, glob, argparse, math, sys

CHUNKSIZE = 400 # Number of pages to fetch at once.
NUMTRIALS = 0 # If a fetch fails due to a timeout, try again at most NUMTRIALS times. 

parser = argparse.ArgumentParser(description='A simple script to download the PDF version of an archival resource hosted by Gallica.')
parser.add_argument('ark', type=str,
                    help='The Archival Resource Key of the resource to download. Can be a Gallica URL (https://gallica.bnf.fr/ark:/12148/bpt6k9764647w) or an ARK URI (ark:/12148/bpt6k9764647w)' )
parser.add_argument('--start', type=int, default=1,
                    help='Index of the first view to download (starts at 1).')
parser.add_argument('--end', type=int, default=0,
                    help='Index of the last view to download.')
parser.add_argument('--split', action='store_true',
                    help='If defined, the script will download the resource in chunks of '+CHUNKSIZE+' views. This is usefull for large resources with more than 1000-1500 views.')
parser.add_argument('outputfile', type=str,
                    help='The output PDF file.') 

def get_pdf(ark, outputfile, from_view, to_view, split):

  r = Resource(ark)
  if not to_view:
    to_view = int(r.pagination_sync().value['livre']['structure']['nbVueImages'])
  data = []

  if split:
    data = split_fetching(r, from_view, to_view)
  else:
    # Try to fetch the whole resource at once. If it fails, try to get the 
    # data in chunks.
    nviews = to_view-from_view+1
    either = fetch_chunk(r, from_view, nviews, NUMTRIALS)
    if either.is_left:
      print("Falling back to chunk download (chunk size: {} views).".format(CHUNKSIZE))
      data = split_fetching(r, from_view, to_view)
    else:
      pdfdata = PdfFileReader(io.BytesIO(either.value))
      data.append(pdfdata)

  save_on_disk(data, outputfile)

def save_on_disk(data, outputfile):
  writer = PdfFileWriter()
  writer.appendPagesFromReader(data[0])
  
  if len(data) > 1:
    # Remove the first two pages added by Gallica from all chunks except the first one
    for part in data[1:]:
      for i in range(2, part.getNumPages()):
        writer.addPage(part.getPage(i))
  
  with open(outputfile, 'wb') as fileobj:
      writer.write(fileobj)
      return

def split_fetching(resource, from_view, to_view ):
  data = []
  # How many jobs do we need to run?
  njobs = math.ceil((to_view-from_view)/CHUNKSIZE)
  for i in range(0, njobs):
    start_at = from_view + i*CHUNKSIZE
    nviews = CHUNKSIZE if (start_at+CHUNKSIZE) <= to_view else to_view-start_at+1
    r = fetch_chunk(resource, start_at, nviews, NUMTRIALS)
    if r.is_left:
      raise Exception("Something went wrong.")
  return data

def fetch_chunk(resource, from_view, nviews, trials_left):
  print("Fetching resource {} from view {} to view {} ({} views)".format(resource.ark.arkid, from_view, from_view+nviews-1, nviews))
  res = resource.content_sync(startview=from_view, nviews=nviews, mode='pdf')
  if res.is_left:
    print("Fetching failed.\n{}\nTrials left: {}".format(str(res.value), trials_left))
    return res if trials_left == 0 else  fetch_chunk(resource, from_view, nviews, trials_left-1)
  return res
  
if __name__ == "__main__":
    args = parser.parse_args()
    if args.end != 0 and args.end < args.start:
      print("Error: end cannot be smaller than start")
      parser.print_help(sys.stderr)
      sys.exit(1)
    get_pdf(args.ark, args.outputfile, args.start, args.end, args.split)