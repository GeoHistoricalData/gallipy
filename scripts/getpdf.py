#!/usr/bin/env python3

"""
A simple command-line tool to download the PDF version of a Gallica resource
when its ARK is known.
"""

import io
import argparse
import math
import sys
import logging
import os
from PyPDF2 import PdfFileReader, PdfFileMerger, PdfFileWriter, PageRange
from gallipy import Resource

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

DEFAULT_NUM_TRIALS = 5

def non_negative_int(value):
    """ Non negative integer"""
    ivalue = int(value)
    if ivalue < 0:
        raise argparse.ArgumentTypeError(
            "Parameter must be a non negative integer, not %d" % value)
    return ivalue

def download_pdf(resource, start, end, blocksize, trials, output_path):
    """ Download the PDF resource in blocks of size blocksize and save it to output_path"""
    partials = []
    try:
        for idx, bound in enumerate(compute_blocks(start, end, blocksize)):
            reason = "Download block "+str(bound)
            either = fetch_block(resource, bound[0], bound[1], trials, reason)
            if either.is_left:
                raise Exception(
                    "Failed to fetch resource {} from view {} to view {}.\nReason: {}".format(
                        resource.arkid,
                        bound[0],
                        bound[0]+bound[1]-1,
                        either.value))
            pdfdata = either.flat_map(lambda v: PdfFileReader(io.BytesIO(v)))
            partial = "{}.{}".format(output_path, idx)
            partials.append(partial)
            write_pdfdata(pdfdata, partial)
        merge_partials(output_path, partials)
    except Exception as ex: # PEP8 will complain (W0703) but we don't care ¯\_(ツ)_/¯
        logging.exception(ex)
        logging.critical("The resource has not been downloaded.")
    finally:
        for partial in partials:
            os.remove(partial)

def clamp(number, smallest, largest):
    """ Clamp a number between smallest and largest"""
    return max(smallest, min(number, largest))

def to_pdffilereader(bdata):
    """Wrap  any pdf binary data in a PdfFileReader object"""
    return PdfFileReader(io.BytesIO(bdata))

def compute_blocks(inf, sup, blocksize):
    """Compute the blocks based on the total view range and a block size"""
    blocks = []
    for i in range(0, math.ceil((sup-inf+1)/blocksize)):
        start = inf+i*blocksize
        nviews = blocksize if (start+blocksize) <= sup else sup-start+1
        blocks.append((start, nviews))
    return blocks

def merge_partials(path, partials):
    """Merge partial pdfs in one single PDF"""
    merger = PdfFileMerger()
    for idx, partial in enumerate(partials):
        # Gallica appends 2 pages to each pdf fetched so we don't write those
        # pagse except for the first partial
        opts = {"pages": PageRange('2:')} if idx else {}
        merger.append(partial, **opts)
    merger.write(path)
    merger.close()

def write_pdfdata(pdffilereader, path):
    """Write a partial file"""
    with open(path, "wb+") as ostream:
        writer = PdfFileWriter()
        writer.appendPagesFromReader(pdffilereader)
        writer.write(ostream)

def fetch_block(resource, from_view, nviews, trials, reason):
    """Retrieve a block of PDF data from Gallica"""
    logging.debug(
        "Fetching resource %s from view %d to view %d",
        resource.ark.arkid,
        from_view,
        from_view+nviews-1)

    res = resource.content_sync(startview=from_view, nviews=nviews, mode="pdf")
    if res.is_left:
        if res.value:
            logging.exception(res.value)
        logging.debug("Reason for calling fetch_block was: <%s>.", reason)
        logging.info("%s attempt left", trials-1)
        if trials > 1:
            return fetch_block(resource, from_view, nviews, trials-1, reason)
    return res

def parse_args():
    """The main : parse arguments and perform some validation before calling download_pdf()"""
    parser = argparse.ArgumentParser(description="""A simple script to download the PDF
                                        of an archival resource hosted on gallica.bnf.fr.""")
    parser.add_argument("ark", type=str,
                        help="""The Archival Resource Key of the resource to download.
                        Can be a Gallica URL (https://gallica.bnf.fr/ark:/12148/bpt6k9764647w) 
                        or an ARK URI (ark:/12148/bpt6k9764647w)""")
    parser.add_argument("-s", "--start", type=non_negative_int, default=0,
                        help="Index of the first view to download (starts at 1).")
    parser.add_argument("-e", "--end", type=non_negative_int, default=0,
                        help="""Index of the last view to download.
                            Default value: the total number of views of this resource.""")
    parser.add_argument("--blocksize", type=non_negative_int, default=0,
                        help="""If defined, the resource will be downloaded
                            in blocks of --blocksize views.
                            A value of 100 seems to minimize timeouts""")
    parser.add_argument("--trials", type=non_negative_int, default=DEFAULT_NUM_TRIALS,
                        help="""If defined, the resource will be downloaded
                            in blocks of --blocksize views.""")
    parser.add_argument("outputfile", type=str,
                        help="The output PDF file.")
    pargs = parser.parse_args()

    resource = Resource(pargs.ark)

    if pargs.end < pargs.start and pargs.end:
        logging.error("Parameter end cannot be smaller than start")
        parser.print_help(sys.stderr)
        sys.exit(1)

    # Ask Gallica"s API to know the total number of views of the resource
    mdata = resource.pagination_sync()
    if mdata.is_left:
        raise mdata.value

    total_views = int(mdata.value["livre"]["structure"]["nbVueImages"])
    start = clamp(pargs.start, 1, total_views)
    end = clamp(pargs.end, start, total_views) if pargs.end else total_views
    nviews = end-start+1
    blocksize = pargs.blocksize if pargs.blocksize or pargs.blocksize > nviews else nviews

    logging.debug(
        "Downloading views %d to %d %s from resource %s with %d views",
        start,
        end,
        "by blocks of size %d" % blocksize if blocksize else "",
        resource.arkid,
        total_views)

    return resource, start, end, blocksize, pargs.trials, pargs.outputfile

if __name__ == "__main__":
    download_pdf(*parse_args())
