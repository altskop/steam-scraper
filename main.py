import argparse
from parser import game_parser
from parser import tags_parser
from parser import db_handler
from parser import common
from parser import update_parser
from parser import rating_parser

DEFAULT_CONFIG_FILE = "config.yml"

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(dest="runtype",
                            help="Runtype for the script."
                                 "- all - Will run parsers for all game info including tags. "
                                 "This will take a very long time so you better find something to do. "
                                 "Watch a movie... or six. Go for a walk. Travel to another country. "
                                 "Find the love of your life. Get married. Get kids. Go through a divorce years later. "
                                 "At least you get to see the kids on the weekends. Remember you left this script"
                                 "running. Come back only to see that it's only 15%% through. - games - Will only "
                                 "parse games info from Steam API. However, the API does not provide tags info "
                                 "so no tags will be parsed. - tags - Will only parse games tags from Steam Web UI. "
                                 "It will only run for the games that have been saved to the database but have no "
                                 "tags saved associated with them. - update - Will loop through every game record already in"
                                 "the dabatase and update it with the latest information."
                                 "",
                            choices=("all", "games", "tags", "update", "rating_update"))
    arg_parser.add_argument("-v", "--verbose",
                            help="Increase verbosity of the script, displaying every record it goes through. "
                                 "By default that output goes to a log file.",
                            action="store_true")
    arg_parser.add_argument("-f", "--force",
                            help="Don't skip records that were previously inaccessible, attempt to retrieve them again.",
                            action="store_true")
    args = arg_parser.parse_args()

    config = common.read_config_file(DEFAULT_CONFIG_FILE)
    db_file = config["DATABASE_FILENAME"]
    db_handler.DBHandler(db_file)

    verbose = args.verbose
    force = args.force
    if args.runtype == "all":
        game_parser = game_parser.GameParser(DEFAULT_CONFIG_FILE, verbose, force)
        game_parser.start_parsing()
        tags_parser = tags_parser.TagsParser(DEFAULT_CONFIG_FILE, verbose)
        tags_parser.start_parsing()
    elif args.runtype == "games":
        game_parser = game_parser.GameParser(DEFAULT_CONFIG_FILE, verbose, force)
        game_parser.start_parsing()
    elif args.runtype == "tags":
        tags_parser = tags_parser.TagsParser(DEFAULT_CONFIG_FILE, verbose)
        tags_parser.start_parsing()
    elif args.runtype == "update":
        upd_parser = update_parser.UpdateGamesParser(DEFAULT_CONFIG_FILE, verbose)
        upd_parser.start_parsing()
    elif args.runtype == "rating_update":
        rating_parser = rating_parser.RatingParser(DEFAULT_CONFIG_FILE, verbose)
        rating_parser.start_parsing()
