#!/usr/bin/env python3

import bibtexparser, argparse
import getpdf, logging

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

parser = argparse.ArgumentParser(description='A simple script to download the PDF version of an archival resource hosted by Gallica.')
parser.add_argument('bibtex', type=str,
                    help='A path to a Bibtex file or a string containing a set of Bibtex entries.' )
parser.add_argument('--key', type=str, default='eprint',
                    help='Name of the Bibtex key containing the ARK.' )
if __name__ == "__main__":
    args = parser.parse_args()

    with open(args.bibtex) as bibtex_file:
        bib_database = bibtexparser.load(bibtex_file)
        for idx, bib in enumerate(bib_database.entries):
          entrytype = bib['ENTRYTYPE']
          bibkey = bib['ID']
          ark = bib[args.key]
          if bib.get('vues'):
            vues = [int(s) for s in bib.get('vues').split('--') if s.isdigit()]
          else:
            vues = [1,0]
          
          logging.info("Downloading {} {}: {} [{}]{}".format(entrytype, idx+1, bibkey, ark, ', views {} to {}'.format(vues[0], vues[1]) if bib.get('vues') else ''))
          name = "{}{}.pdf".format(bibkey,'_'+str(vues[0])+'_'+str(vues[1]) if bib.get('vues') else '')
          getpdf.download_pdf(ark, name, vues[0], vues[1])