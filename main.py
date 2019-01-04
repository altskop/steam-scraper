import argparse
from scraper import game_scraper
from scraper import tags_scraper
from scraper import db_handler
from scraper import common
from scraper import games_update_scraper
from scraper import rating_scraper

DEFAULT_CONFIG_FILE = "config.yml"

if __name__ == "__main__":
    arg_scraper = argparse.ArgumentParser()
    arg_scraper.add_argument(dest="runtype",
                            help="Runtype for the script."
                                 "- all - Will run scrapers for all game info including tags. "
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
    arg_scraper.add_argument("-v", "--verbose",
                            help="Increase verbosity of the script, displaying every record it goes through. "
                                 "By default that output goes to a log file.",
                            action="store_true")
    arg_scraper.add_argument("-f", "--force",
                            help="Don't skip records that were previously inaccessible, attempt to retrieve them again.",
                            action="store_true")
    args = arg_scraper.parse_args()

    config = common.read_config_file(DEFAULT_CONFIG_FILE)
    db_file = config["DATABASE_FILENAME"]
    db_handler.DBHandler(db_file)

    verbose = args.verbose
    force = args.force
    if args.runtype == "all":
        game_scraper = game_scraper.GameScraper(DEFAULT_CONFIG_FILE, verbose, force)
        game_scraper.start_scraping()
        tags_scraper = tags_scraper.TagsScraper(DEFAULT_CONFIG_FILE, verbose)
        tags_scraper.start_scraping()
    elif args.runtype == "games":
        game_scraper = game_scraper.GameScraper(DEFAULT_CONFIG_FILE, verbose, force)
        game_scraper.start_scraping()
    elif args.runtype == "tags":
        tags_scraper = tags_scraper.TagsScraper(DEFAULT_CONFIG_FILE, verbose)
        tags_scraper.start_scraping()
    elif args.runtype == "update":
        upd_scraper = games_update_scraper.UpdateGamesScraper(DEFAULT_CONFIG_FILE, verbose)
        upd_scraper.start_scraping()
    elif args.runtype == "rating_update":
        rating_scraper = rating_scraper.RatingScraper(DEFAULT_CONFIG_FILE, verbose)
        rating_scraper.start_scraping()
