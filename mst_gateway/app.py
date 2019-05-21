import sys
import getopt
from .gateway import Gateway
from .exceptions import GatewayError, SignalInterrupt
from .config import read_config_file
from .logging import create_logger
from .version import VERSION


def help_message():
    return """mst_gateway [-h] [-v] -c <config_path>
Run mstrader gateway worker (version: {})
    -c <config_path> path to config file
    -h - show help message
    -v - show version""".format(VERSION)


def parse_args():
    args = {
        'config_path': None
    }
    try:
        opts = getopt.getopt(sys.argv[1:], "hvc:", ["help", "version"
                                                    "config="])
        for opt, arg in opts[0]:
            if opt in ("-h", "--help"):
                print(help_message())
                sys.exit(4)
            elif opt in ("-c", "--config"):
                args['config_path'] = arg
            elif opt in ("-v", "--version"):
                print("Version: {}".format(VERSION))
                sys.exit(4)
    except getopt.GetoptError:
        raise GatewayError("Wrong parameters! please try again with another args."
                           "\n{}".format(help_message()))

    if not args['config_path']:
        raise GatewayError("Configuration file is not defined")
    return args


def main():
    logger = create_logger(name='mst.gateway')
    try:
        args = parse_args()
        logger.info("Starting...")
        config = read_config_file(args['config_path'], app_prefix='MST_LOADER')
        logger = create_logger(
            name='mst.data-loader',
            logfile=config.get('main', 'logfile', 'STDOUT'),
            loglevel=config.get('main', 'loglevel', 'INFO'))
        logger.info("Configuration file: %s", args['config_path'])
        with Gateway(config=config, logger=logger) as loader:
            loader.run()
    except KeyboardInterrupt:
        logger.info("Interrupted by keyboard")
    except SignalInterrupt as exc:
        logger.info("Got signal: %s", exc)
    except GatewayError as exc:
        logger.error("Some error occured. Details: %s", exc)
    logger.info("Exiting...")
