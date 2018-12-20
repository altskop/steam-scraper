import requests
import sqlite3
from . import common, parser
from bs4 import BeautifulSoup
from time import sleep


class TagsParser(parser.Parser):

    def __init__(self, config_filename: str, verbose: bool):
        parser.Parser.__init__(self, config_filename, verbose)
        self.APP_DETAILS_URL = "https://store.steampowered.com/app/"
        self.succeed = 0
        self.fail = 0

    def get_records_list(self):
        conn = sqlite3.connect(self.DATABASE_FILE)
        with conn:
            c = conn.cursor()
            stmt = """
                    SELECT t1.id
                    FROM games t1
                    LEFT JOIN tags t2 ON t2.gameid = t1.id
                    WHERE t2.gameid IS NULL;
                    """
            c.execute(stmt)
            result = [item[0] for item in c.fetchall()]
            return result

    def new_record(self, tags, appid):
        """
        Insert new records into tags table for a given appid. There can be
        (and should be) multiple records for any application.
        :param tags: array of tags
        :param appid: id of an app
        """
        conn = sqlite3.connect(self.DATABASE_FILE)
        with conn:
            c = conn.cursor()

            if tags is not None:
                if len(tags) > 0:
                    for tag in tags:
                        stmt = "insert into tags (name, gameid) values(?,?)"
                        params = (tag, appid)
                        c.execute(stmt, params)
                    self.printc("Records for #" + str(appid) +" inserted.", common.Color.OKGREEN)

    def get_record(self, appid):
        self.printc("Running ID " + str(appid) + "...", common.Color.ENDC)
        url = self.APP_DETAILS_URL + str(appid)
        attempts = 0
        while True:
            try:
                resp = requests.get(url=url)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.content, 'html.parser')
                    html_tags = soup.find_all("a", class_="app_tag")
                    tags = []
                    for tag in html_tags:
                        tags.append(tag.get_text().strip())
                    self.succeed += 1
                    return tags
                elif resp.status_code == 429:
                    attempts += 1
                    self.printc("\rToo many requests, waiting... #" + str(attempts), common.Color.FAIL)
                    sleep(self.TIMEOUT)
                elif resp.status_code == 404:
                    self.printc("\rNo such page exists. #", common.Color.FAIL)
                    self.fail += 1
                    return None
            except requests.ConnectionError as e:
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
