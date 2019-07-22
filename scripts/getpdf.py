#!/usr/bin/env python3

from gallipy import Resource, Ark
from gallipy.monadic import Left
from PyPDF2 import PdfFileReader, PdfFileMerger, PdfFileWriter
import io, glob, argparse, math, sys, logging, os

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

NUMTRIALS = 5 # If a fetch fails due to a timeout, try again at most NUMTRIALS times.

def nnint(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("Parameter must be a non negative integer, not %s" % value)
    return ivalue


def build_query_params(args):
    r = Resource(args.ark)

    if args.start < args.end:
      logging.error("Parameter end cannot be smaller than start")
      parser.print_help(sys.stderr)
      sys.exit(1)

    # We ask the user for "start and ""end" views because it's easier to understand, but Gallica takes "start" and "nviews"
    # Ask Gallica's API to know the total number of views of the resource
    mdata = r.pagination_sync()
    if mdata.is_left:
      raise mdata.value
    total_views = int(mdata.value['livre']['structure']['nbVueImages'])

    start = clamp(args.start, 1, total_views)

    if not args.end:
        end = total_views
    else:
        end = clamp(args.end, start, total_views)

    nviews = end-start+1
    if not args.blocksize or args.blocksize > nviews:
        blocksize = nviews
    else:
        blocksize = args.blocksize

    return r, start, end, blocksize

def download_pdf(ark, start, end, blocksize, outputfile):
    partfiles = []
    try:
        for idx, bound in enumerate(compute_blocks(start, end, blocksize)):
          reason = "Download block "+str(bound)
          either = fetch_block(r, bound[0], bound[1], NUMTRIALS, reason)
          if either.is_left:
            raise Exception("Failed to fetch resource {} from view {} to view {}.\nReason: ".format(r.arkid, bound[0], bound[0]+bound[1]-1, either.value))
          else:
            pdfdata = to_pdffilereader(either.value)
            partfile = partfile_path(outputfile, idx)
            partfiles.append(partfile)
            write_to_file(pdfdata, partfile, idx)
        merge_partfiles(outputfile, partfiles)
    except Exception as e:
        logging.exception(e)
        logging.critical("The resource has not been downloaded.")
    finally:
        [os.remove(partfile) for partfile in partfiles]

def clamp(n, smallest, largest): return max(smallest, min(n, largest))

def to_pdffilereader(bdata): return PdfFileReader(io.BytesIO(bdata))

def partfile_path(outputfile, block_idx): return "{}.part{}".format(outputfile, block_idx)

def compute_blocks(a,b, blocksize):
  blocks = []
  for i in range(0, math.ceil((b-a+1)/blocksize)):
    start = a+i*blocksize
    nviews = blocksize if (start+blocksize) <= b else b-start+1
    blocks.append((start, nviews))
  return blocks

def merge_partfiles(outfile, partfiles):
    merger = PdfFileMerger()
    for partfile in partfiles:
        merger.append(partfile)
    merger.write(outfile)
    merger.close()


def write_to_file(pdfdata, outfile, block_idx):
    with open(outfile,"wb+") as ostream:
        writer = PdfFileWriter()
        start = 2 if block_idx > 0 else 1
        for i in range(start, pdfdata.getNumPages()):
          writer.addPage(pdfdata.getPage(i))
        writer.write(ostream)

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

    parser = argparse.ArgumentParser(description='A simple script to download the PDF version of an archival resource hosted by Gallica.')
    parser.add_argument('ark', type=str,
                        help='The Archival Resource Key of the resource to download. Can be a Gallica URL (https://gallica.bnf.fr/ark:/12148/bpt6k9764647w) or an ARK URI (ark:/12148/bpt6k9764647w)' )
    parser.add_argument('-s', '--start', type=nnint, default=0,
                        help='Index of the first view to download (starts at 1).')
    parser.add_argument('-e', '--end', type=nnint, default=0,
                        help='Index of the last view to download. Default value: the total number of views of this resource.')
    parser.add_argument('--blocksize', type=nnint, default=0,
                        help='If defined, the resource will be downloaded in blocks of --blocksize views.')
    parser.add_argument('outputfile', type=str,
                        help='The output PDF file.')
    args = parser.parse_args()
    r, start, end, blocksize = build_query_params(args)
    download_pdf(r, start, end, blocksize, args.outputfile)
