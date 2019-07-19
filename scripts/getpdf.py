#!/usr/bin/env python3

from gallipy import Resource, Ark
from gallipy.monadic import Left
from PyPDF2 import PdfFileReader, PdfFileWriter
import io, glob, argparse, math, sys, logging

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

BLOCKSIZE = 300 # Default number of pages to fetch at once.
NUMTRIALS = 5 # If a fetch fails due to a timeout, try again at most NUMTRIALS times.

parser = argparse.ArgumentParser(description='A simple script to download the PDF version of an archival resource hosted by Gallica.')
parser.add_argument('ark', type=str,
                    help='The Archival Resource Key of the resource to download. Can be a Gallica URL (https://gallica.bnf.fr/ark:/12148/bpt6k9764647w) or an ARK URI (ark:/12148/bpt6k9764647w)' )
parser.add_argument('-s', '--start', type=int, default=1,
                    help='Index of the first view to download (starts at 1). Default value: 1.')
parser.add_argument('-e', '--end', type=int, default=0,
                    help='Index of the last view to download. Default value: the total number of views of this resource.')
parser.add_argument('--blocksize', type=int,
                    help='If defined, the resource will be downloaded in blocks of --blocksize views. Default value: '+str(BLOCKSIZE))
parser.add_argument('outputfile', type=str,
                    help='The output PDF file.')

# Pass to_view = 0 to download all pages after from_view
def download_pdf(ark, outputfile, from_view, to_view, blocksize=BLOCKSIZE, one_step_download=True):
  try:
    # Check immediately if the output fule is writeable. If not, there's no need to go further.
    with open(outputfile, 'wb') as outstream:
      r = Resource(ark)

      # Clamps the view bounds to [1,total_views] if necessary. Total_views is retrieved
      # from the resource's metada.
      mdata = r.pagination_sync()
      if mdata.is_left:
        raise mdata.value
      total_views = int(mdata.value['livre']['structure']['nbVueImages'])
      start = clamp(from_view, 1, total_views)
      end = clamp(to_view, 1, total_views)  if to_view else total_views

      if one_step_download:
        reason = "Download the entire resource at once."
        either = fetch_block(r, start, end-start+1, NUMTRIALS, reason)
        if either.is_left:
        # If the user wanted to download the whole resource in one bug block but it failed,
        # try again with multiple small queries.
          logging.exception("Fetching Failed.\nReason: {}.\nTry again, but this time download the resource in smaller blocks...".format(either.value))
        else:
          return write_to_stream(to_pdffilereader(either.value), outstream, False)

      for idx, bound in enumerate(compute_blocks(start, end, blocksize)):
        reason = "Download block "+str(bound)
        either = fetch_block(r, bound[0], bound[1], NUMTRIALS, reason)
        if either.is_left:
          raise Exception("Failed to fetch resource {} from view {} to view {}.\nReason: ".format(r.arkid, bound[0], bound[0]+bound[1]-1, either.value))
        else:
          write_to_stream(to_pdffilereader(either.value), outstream, idx > 0)
  except Exception as e:
    logging.critical(str(e))
    logging.critical("The resource has not been downloaded.")

def clamp(n, smallest, largest): return max(smallest, min(n, largest))

def to_pdffilereader(bdata): return PdfFileReader(io.BytesIO(bdata))

def compute_blocks(a,b, blocksize):
  blocks = []
  for i in range(0, math.ceil((b-a+1)/blocksize)):
    start = a+i*blocksize
    nviews = blocksize if (start+blocksize) <= b else b-start+1
    blocks.append((start, nviews))
  return blocks

def write_to_stream(pdfdata, outstream, remove_gallica_pages):
  writer = PdfFileWriter()
  start = 2 if remove_gallica_pages else 1
  for i in range(start, pdfdata.getNumPages()):
    writer.addPage(pdfdata.getPage(i))
  writer.write(outstream)

def fetch_block(resource, from_view, nviews, trial, reason):
  logging.debug("Fetching resource {} from view {} to view {} ({} views -- trial {})".format(resource.ark.arkid, from_view, from_view+nviews-1, nviews, NUMTRIALS-trial+1))
  res = resource.content_sync(startview=from_view, nviews=nviews, mode='pdf')
  if res.is_left and trial > 0:
    logging.exception(res.value)
    logging.debug("Reason for calling fetch_block was: <"+reason+">.")
    logging.debug("Trials left: {}".format(trial-1))
    fetch_block(resource, from_view, nviews, trial-1, reason)
  return res

if __name__ == "__main__":
    args = parser.parse_args()

    if args.end < 0:
      logging.error("Parameter end must be a positive integer.")
      parser.print_help(sys.stderr)
      sys.exit(1)

    if args.start < 0:
      logging.error("Parameter start must be a positive integer.")
      parser.print_help(sys.stderr)
      sys.exit(1)

    if args.end and args.end < args.start:
      logging.error("Parameter end cannot be smaller than start")
      parser.print_help(sys.stderr)
      sys.exit(1)

    blocksize = clamp(args.blocksize, 1, 100000)

    download_pdf(args.ark, args.outputfile, args.start, args.end, blocksize, args.blocksize <= 0 )
