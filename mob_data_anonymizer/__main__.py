import logging

from mob_data_anonymizer import cli, __app_name__


def main():
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO)

    cli.app(prog_name=__app_name__)


if __name__ == "__main__":
    main()
