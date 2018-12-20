import requests
import sqlite3
import re
from time import sleep
from . import common, parser


class GameParser(parser.Parser):

    def __init__(self, config_filename: str, verbose: bool):
        parser.Parser.__init__(self, config_filename, verbose)
        self.APP_DETAILS_URL = "https://store.steampowered.com/api/appdetails?appids="

    def get_records_list(self):
        games_list = self.get_records_list_from_json(self.ALLGAMES_FILE)
        return self.check_all_records(games_list)

    @staticmethod
    def split_languages(string):
        """
        Helper method to split a string of languages into an array.
        """
        if "<br>" in string:
            string = string.split("<br>", 1)[0]
        string = re.sub('\<\S+\>', '', string)
        string = string.replace("*", "")
        languages = string.split(",")
        result_set = []
        for entry in languages:
            entry = entry.strip()
            result_set.append(entry)
        return result_set

    def check_all_records(self, games):
        """
        Prior to running queries, we first need to build a list of applications
        to run queries on. To do that, we pull all appids from allgames.json and
        choose those that satisfy our conditions (already in DB and don't have any
        tags recorded). A list of those apps is then returned.
        :param games: list of games from allgames.json
        :return: list of game ids satisfying our requirements
        """
        conn = sqlite3.connect(self.DATABASE_FILE)
        result = []
        for game in games:
            appid = str(game["appid"])
            if self.is_not_recorded(conn, appid) is True:
                result.append(appid)
        result = sorted(result, key=int)
        return result

    @staticmethod
    def is_not_recorded(conn, appid):
        """
        This method will check if the database already contains the record
        of an application with a provided AppId.

        The intended behaviour for this script is to only record tags when the
        following condition is true:
            - There are no existing records for a given application in games table

        :param conn: sqlite connection to utilize
        :param appid: id of an application to run a check for
        :return: True if satisfies the conditions, False otherwise
        """
        with conn:
            c = conn.cursor()
            stmt = "select id from games where id=?"
            params = (appid,)
            c.execute(stmt, params)
            result = c.fetchall()
            return len(result) == 0

    def new_record(self, data, appid):
        """
        Inserts a new record for a game using the data retrieved from
        the json object retrieved from Steam API. There can only be one
        record for an ID.
        :param data:
        :param appid:
        :return:
        """
        conn = sqlite3.connect(self.DATABASE_FILE)
        with conn:
            c = conn.cursor()

            type = common.get_from_json(data, "type")
            game_name = common.get_from_json(data, "name")
            required_age = common.get_from_json(data, "required_age")
            is_free = common.str_to_bool(common.get_from_json(data, "is_free"))

            full_game = common.get_from_json(data, "fullgame")
            if full_game is not None:
                full_game_id = full_game["appid"]
            else:
                full_game_id = None

            detailed_description = common.get_from_json(data, "detailed_description")
            about_the_game = common.get_from_json(data, "about_the_game")
            short_description = common.get_from_json(data, "short_description")

            supported_languages = common.get_from_json(data, "supported_languages")  # string to parse
            if supported_languages is not None:
                languages = self.split_languages(supported_languages)
            else:
                languages = None

            developers = common.get_from_json(data, "developers")  # json array?
            publishers = common.get_from_json(data, "publishers")  # json array?

            price_overview = common.get_from_json(data, "price_overview")
            if price_overview is not None:
                price = price_overview["initial"]
            else:
                price = 0

            platforms = common.get_from_json(data, "platforms")  # json array?
            metacritic = common.get_from_json(data, "metacritic")  # json array?
            categories = common.get_from_json(data, "categories")  # json array?
            genres = common.get_from_json(data, "genres")  # json array?

            recommendations = common.get_from_json(data, "recommendations")
            if recommendations is not None:
                recommendations = recommendations["total"]
            else:
                recommendations = 0

            screenshots = common.get_from_json(data, "screenshots")  # json array?
            if screenshots is not None:
                screenshots_num = len(screenshots)
            else:
                screenshots_num = 0

            movies = common.get_from_json(data, "movies")  # json array?
            if movies is not None:
                movies_num = len(movies)
            else:
                movies_num = 0

            achievements = common.get_from_json(data, "achievements")
            if achievements is not None:
                achievements = achievements["total"]
            else:
                achievements = 0

            release_date = common.get_from_json(data, "release_date")
            if release_date is not None:
                release_date = release_date["date"]
            else:
                release_date = None

            stmt = "insert into games (id," \
                   " name, type, required_age," \
                   " is_free, full_game_id, detailed_description," \
                   " about_the_game, short_description, price," \
                   " recommendations, release_date, screenshots," \
                   " movies, achievements) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
            params = (appid, game_name, type, required_age, is_free, full_game_id, detailed_description,
                      about_the_game, short_description, price, recommendations, release_date, screenshots_num,
                      movies_num, achievements)
            c.execute(stmt, params)

            if languages is not None:
                for language in languages:
                    stmt = "insert into languages (name, gameid) values(?,?)"
                    params = (language, appid)
                    c.execute(stmt, params)

            if developers is not None:
                for dev in developers:
                    stmt = "insert into developers (name, gameid) values(?,?)"
                    params = (dev, appid)
                    c.execute(stmt, params)

            if publishers is not None:
                for pub in publishers:
                    stmt = "insert into publishers (name, gameid) values(?,?)"
                    params = (pub, appid)
                    c.execute(stmt, params)

            if platforms is not None:
                for platform in platforms:
                    stmt = "insert into platforms (name, status, gameid) values(?,?,?)"
                    status = platforms[platform]
                    params = (platform, status, appid)
                    c.execute(stmt, params)

            if metacritic is not None:
                stmt = "insert into metacritic (score, url, gameid) values(?,?,?)"
                score = common.get_from_json(metacritic, "score")
                url = common.get_from_json(metacritic, "url")
                params = (score, url, appid)
                c.execute(stmt, params)

            if categories is not None:
                for category in categories:
                    stmt = "insert into categories (name, gameid) values(?,?)"
                    name = category["description"]
                    params = (name, appid)
                    c.execute(stmt, params)

            if genres is not None:
                for genre in genres:
                    stmt = "insert into genres (name, gameid) values(?,?)"
                    name = genre["description"]
                    params = (name, appid)
                    c.execute(stmt, params)

            self.printc("Record #" + str(appid) +" (" + game_name +") inserted.", common.Color.OKGREEN)

    def get_record(self, appid):
        self.printc("Running ID " + appid + "...", common.Color.ENDC)
        url = self.APP_DETAILS_URL + appid
        attempts = 0
        while True:
            try:
                resp = requests.get(url=url)
                if resp.status_code == 200:
                    data = resp.json()[appid]
                    if data["success"] is not False:
                        return data["data"]
                    else:
                        return None
                elif resp.status_code == 429:
                    attempts += 1
                    self.printc("\rToo many requests, waiting... #" + str(attempts), common.Color.FAIL)
                    sleep(self.TIMEOUT)
            except Exception as e:
                attempts += 1
                self.printc("\rError occurred " + str(e.__class__) + ". #" + str(attempts), common.Color.FAIL)
                sleep(self.TIMEOUT)

    def on_finished(self):
        self.printc("", common.Color.ENDC)
        common.printcolor("\n\nExecution finished. New records: " + str(self.current), common.Color.OKBLUE)
        print("Execution time: " + common.seconds_to_string(common.get_elapsed_time(self.start_time)))

