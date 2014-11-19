import logging

from argh import ArghParser

from ._version import __version__
from .operations import (
    push,
    remove,
    list_,
)
from .service import service


def version():
    print(__version__)


def set_loglevel(namespace):
    loglevel = getattr(namespace, 'loglevel')
    logging.basicConfig(
        format='%(asctime)s %(levelname)6s: %(msg)s',
        level=getattr(logging, loglevel.upper()))
    # Keep some talkative modules quiet
    for logger_name in ['asyncio_redis', 'asyncio']:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.WARN)


if __name__ == '__main__':
    parser = ArghParser(prog='kamikaze')
    parser.add_argument(
        '--loglevel', help='Set the logging level', default='INFO',
        choices=logging._nameToLevel.keys())
    parser.add_commands([service, push, remove, list_, version])
    parser.dispatch(pre_call=set_loglevel)
