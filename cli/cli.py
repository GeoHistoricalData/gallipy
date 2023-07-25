import click
import httpx
from gallipy import services
from PyPDF2 import PdfWriter
import colorlog
from lark.exceptions import UnexpectedInput
import logging

handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter("%(log_color)s%(message)s"))

logger = colorlog.getLogger("cli")
logger.addHandler(handler)


@click.group()
def gallipy():
    pass


@gallipy.command()
@click.argument("ark")
@click.option(
    "-s",
    "--start",
    help="View number of the first page to download. Defaults to 1.",
    type=click.IntRange(1),
    default=1,
)
@click.option(
    "-e",
    "--end",
    help="View number of the last page to download. Defaults to 1.",
    type=click.IntRange(1),
    default=1,
)
def pdf(ark: str, start: int, end: int):
    """Pdf export of a resource published on Gallica identified by ARK.

    Specify a range of pdf views with `--start` and `--end` to download only a portion of the resource.
    Omitting `--end` is equivalent to asking for all pages from `--start`.
    """
    try:
        if end < start:
            raise click.BadOptionUsage(
                option_name="end",
                message="--end must be greater than or equals to --start",
            )
        try:
            with httpx.Client(timeout=10) as c:
                pdfdata = services.PDF(ark=ark).fetch(c, start, end)
                with open("/tmp/test.pdf", "wb") as ostream:
                    writer = PdfWriter()
                    writer.append_pages_from_reader(pdfdata)
                    writer.write(ostream)
        except UnexpectedInput:
            raise click.BadArgumentUsage(f"Failed to parse the ARK identifier `{ark}`.")
    except Exception as e:
        logger.error(e)


# Entry point
gallipy()
