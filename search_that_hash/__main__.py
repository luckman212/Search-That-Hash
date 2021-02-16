import json
import sys
import toml

import click

from search_that_hash.cracker import cracking
from search_that_hash import config_object
from search_that_hash import printing
from concurrent.futures import ThreadPoolExecutor

import logging
import coloredlogs

@click.command()
@click.option("--text", "-t", type=str, help="Crack a single hash")
@click.option(
    "-f",
    "--file",
    type=click.File("r"),
    required=False,
    help="The file of hashes, seperated by newlines.",
)
@click.option("-w", "--wordlist", type=str, required=False, help="The wordlist.")
@click.option("--timeout", type=int, help="Choose timeout time in second", default=1)
@click.option("--hashcat", is_flag=True, help="Runs Hashcat instead of John")
@click.option("-g", "--greppable", is_flag=True, help="Used to grep")
@click.option(
    "--hashcat_binary",
    type=str,
    required=False,
    help="Location of hashcat / john folder (if using windows)",
)
@click.option(
    "--offline",
    "-o",
    is_flag=True,
    default=False,
    type=bool,
    help="Use offline mode. Does not search for hashes.",
)
@click.option(
    "-v",
    "--verbose",
    count=True,
    type=int,
    help="Turn on debugging logs. -vv for max",
)
@click.option("--accessible", is_flag=True, help="Makes the output accessible.")
@click.option("--no-banner", is_flag=True, help="Doesn't print banner.")

def main(**kwargs):
    """
    Search-That-Hash - The fastest way to crack any hash.
    \n
    GitHub:\n
        https://github.com/HashPals/Search-That-Hash\n
    Discord:\n
        https://discord.gg/CswayhQ8Ru
    \n
    Usage:
    \n
        sth --text "5f4dcc3b5aa765d61d8327deb882cf99"
    """

    #### LOGGING
    
    levels = {1:logging.WARNING,2:logging.INFO,3:logging.DEBUG}
    try:
        coloredlogs.install(level=levels[kwargs['verbose']])
    except:
        # Verobosity was not given so it removes logging
        coloredlogs.install(level=logging.CRITICAL)

    logging.debug("Updated logging level")
    logging.info("Called config updater")

    #### UPDATING CONFIG

    config = config_object.cli_config(kwargs)

    #### BANNER

    if not kwargs["greppable"] and not kwargs["accessible"] and not kwargs["no_banner"]:
        logging.info("Printing banner")
        printing.Prettifier.banner()

    #### ASSIGNING VARIBLES

    hash_processes = []
    results = []
    searcher = cracking.Searcher(config)

    #### CRACKING

    for chash, types in config['hashes'].items():
        if types == []:
            if chash == '':
                continue ## BUG - NTH or STH not sure returns a hash as '' with types of []
            if not config['greppable']:
                printing.Prettifier.error_print("No types found for this hash.", chash)
            continue

        hash_processes.append(cracking.Searcher.main(searcher, chash, types))
        
        #### OUTPUTTING

        chash = list(hash_processes[-1].keys())[0]
        result = hash_processes[-1][chash]

        if result == None and not config['greppable']:
             printing.Prettifier.error_print("Could not crack hash.", chash)
             continue

        if not config['greppable']:
            printing.Prettifier.one_print(chash, result)
        
    if kwargs["greppable"]:
        logging.info("Printing greppable results")
        printing.Prettifier.greppable_print(hash_processes)

    exit(0)

if __name__ == "__main__":
    main()
