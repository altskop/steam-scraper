from abc import ABC, abstractmethod
import time
import os
import sys
import json
import urllib
from . import common
from urllib import request
from datetime import datetime
from .date_formatter import DateFormatter


class Scraper(ABC):
    """
    Base class for Scraper.
    """

    def __init__(self, config_filename: str, verbose: bool):
        print("Initialising scraper...")

        self.date_formatter = DateFormatter("%Y-%m-%d")
        self.date_formatter.add_input_format("%b %d, %Y")
        self.date_formatter.add_input_format("%B %d, %Y")
        self.date_formatter.add_input_format("%d %b, %Y")
        self.date_formatter.add_input_format("%d %B, %Y")
        self.date_formatter.add_input_format("%b %d %Y")
        self.date_formatter.add_input_format("%B %d %Y")
        self.date_formatter.add_input_format("%d %b %Y")
        self.date_formatter.add_input_format("%d %B %Y")
        self.date_formatter.add_input_format("%b %Y")

        self.config = common.read_config_file(config_filename)
        self.TIMEOUT = int(self.config["TIMEOUT"])
        self.DATABASE_FILE = self.config["DATABASE_FILENAME"]
        self.ALLGAMES_FILE = self.config["ALLGAMES_FILENAME"]
        self.starting_number = int(self.config["STARTING_APPID"])
        self.JSON_MAX_FILE_AGE = int(self.config["JSON_MAX_FILE_AGE"])
        self.LOGFILE = self.config["LOGFILE_NAME"]

        self.verbose = verbose
        if self.verbose is False: # If verbosity is off, create a new logfile
            with open(self.LOGFILE, "w") as logfile:
                logfile.write("")

        self.ALL_GAMES_API_URL = "http://api.steampowered.com/ISteamApps/GetAppList/v0002/?key=STEAMKEY&format=json"
        self.start_time = 0
        self.current = 0
        self.games_list = self.get_records_list()
        self.total = len(self.games_list)
        print("Scraper initialised.")

    @abstractmethod
    def get_records_list(self):
        """
        This method should get all the records to run scraping on. It
        can do that in various ways such as JSON scraping, database
        quering etc.
        :return: type Sized of records
        """
        return []

    def get_records_list_from_json(self, filename):
        if not os.path.isfile(filename):
            print("Could not locate JSON file with all apps. Attempting to pull one from Steam...")
            urllib.request.urlretrieve(self.ALL_GAMES_API_URL, filename)
        else:
            mod_time = os.path.getmtime(filename)
            mod_date = datetime.utcfromtimestamp(mod_time)
            current_date = datetime.now()
            delta = current_date - mod_date
            if delta.days > self.JSON_MAX_FILE_AGE:
                common.printcolor("JSON file is "+str(delta.days)+" days old. "
                                  "Newer records might be missing. Would you like to get the newest file?",
                                  common.Color.WARNING)
                choice = input("Type in \"yes\" to download newest records file.")
                if choice.lower() == "yes":
                    urllib.request.urlretrieve(self.ALL_GAMES_API_URL, filename)
            else:
                print("JSON file is "+str(delta.days)+" days old.")

        with open(filename, 'r') as f:
            applist = json.load(f)
            games = applist["applist"]["apps"]
            return games

    def start_scraping(self):
        self.start_time = time.time()
        print("Starting scraping...")
        if len(self.games_list)>0:
            for entry in self.games_list:
                if int(entry) >= self.starting_number:
                    data = self.get_record(entry)
                    if data is not None:
                        self.new_record(data, entry)

                self.current = self.current + 1
            self.on_finished()
        else:
            print("No records to scrape. Exiting.")

    @abstractmethod
    def on_finished(self):
        """
        This method is called after scraping is finished in start_scraping().
        Implementations may choose to display various statistics or just an
        exit message.
        """
        pass

    @abstractmethod
    def get_record(self, appid):
        """
        This method is called to retrieve some data using a provided appid. It
        may be an API or a web call, DB query etc. depending on implementation.
        :param appid: id of an app to retrieve data on
        :return: retrieved data
        """
        pass

    @abstractmethod
    def new_record(self, data, appid):
        """
        This method should be called to create a record etc. using appid and
        its relevant data. For example, it could be inserted in a database.
        :param data: some data originating from get_record()
        :param appid: id of an app
        """
        pass

    def printc(self, string, color):
        """
        Helper function used to print text and the progress bar. Also
        supports different text colors.
        :param string: text to print
        :param color: an instance of Color to use
        """
        percent = common.percentage(self.current, self.total)
        sys.stdout.write(common.ANSISequence.ERASE_LINE)
        if self.verbose:
            sys.stdout.write(color + string + common.Color.ENDC + "\n")
        else:
            with open(self.LOGFILE, "a") as logfile:
                logfile.write(string+"\n")

        sys.stdout.write(common.Color.BOLD + "[%-50s] %d%%" % ('=' * int(percent / 2), percent) + common.Color.ENDC)
        sys.stdout.flush()



