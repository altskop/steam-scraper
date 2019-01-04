import requests
import sqlite3
from . import common, scraper
from bs4 import BeautifulSoup
from time import sleep
import re


class RatingScraper(scraper.Scraper):

    def __init__(self, config_filename: str, verbose: bool):
        scraper.Scraper.__init__(self, config_filename, verbose)
        self.APP_DETAILS_URL = "https://store.steampowered.com/app/"
        self.succeed = 0
        self.fail = 0
        self.percentage_regex = re.compile("(\d+)%")

    def get_records_list(self):
        conn = sqlite3.connect(self.DATABASE_FILE)
        with conn:
            c = conn.cursor()
            stmt = """
                    SELECT id from games;
                    """
            c.execute(stmt)
            result = [item[0] for item in c.fetchall()]
            return result

    def new_record(self, rating, appid):
        """
        Insert new records into tags table for a given appid. There can be
        (and should be) multiple records for any application.
        :param rating: rating of an app
        :param appid: id of an app
        """
        conn = sqlite3.connect(self.DATABASE_FILE)
        with conn:
            c = conn.cursor()

            stmt = "update games set rating=? where id=?"
            params = (rating, appid)
            c.execute(stmt, params)
            self.succeed += 1
            self.printc("Rating "+str(rating)+"% for #" + str(appid) + " inserted.", common.Color.OKGREEN)

    def get_record(self, appid):
        self.printc("Running ID " + str(appid) + "...", common.Color.ENDC)
        url = self.APP_DETAILS_URL + str(appid)
        attempts = 0
        while True:
            try:
                resp = requests.get(url=url)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.content, 'html.parser')
                    html_tags = soup.find_all("div", class_="user_reviews_summary_row")
                    tags = []
                    for tag in html_tags:
                        tags.append(tag.get_text(strip=True).strip())
                    try:
                        match = re.search(self.percentage_regex, tags[1])
                        if match:
                            return match.group(1)
                        return None
                    except IndexError or AttributeError:
                        return None
                elif resp.status_code == 429:
                    attempts += 1
                    self.printc("\rToo many requests, waiting... #" + str(attempts), common.Color.FAIL)
                    sleep(self.TIMEOUT)
                elif resp.status_code == 404:
                    self.printc("\rNo such page exists. #", common.Color.FAIL)
                    self.fail += 1
                    return None
            except requests.ConnectionError or ConnectionResetError as e:
                attempts += 1
                self.printc("\rError occurred " + str(e.__class__) + ". #" + str(attempts), common.Color.FAIL)
                sleep(self.TIMEOUT)
            except requests.TooManyRedirects as e:
                attempts += 1
                self.printc("\rToo many redirects. #" + str(attempts), common.Color.FAIL)
                self.printc("Can't get record, moving on.", common.Color.FAIL)
                self.fail += 1
                return None

    def on_finished(self):
        self.printc("", common.Color.ENDC)
        common.printcolor("\n\nExecution finished. Updated records: " + str(self.succeed) +
                          " | Failed: " + str(self.fail) + " | Total: " + str(self.total), common.Color.OKBLUE)
        print("Execution time: " + common.seconds_to_string(common.get_elapsed_time(self.start_time)))
