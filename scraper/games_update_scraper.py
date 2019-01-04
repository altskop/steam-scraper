import requests
import sqlite3
from . import common, scraper
from time import sleep
import re


class UpdateGamesScraper(scraper.Scraper):

    def __init__(self, config_filename: str, verbose: bool):
        scraper.Scraper.__init__(self, config_filename, verbose)
        self.APP_DETAILS_URL = "https://store.steampowered.com/api/appdetails?appids="

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

    def get_records_list(self):
        conn = sqlite3.connect(self.DATABASE_FILE)
        with conn:
            c = conn.cursor()
            stmt = """
                    SELECT id
                    FROM games;
                    """
            c.execute(stmt)
            result = [item[0] for item in c.fetchall()]
            return result

    def new_record(self, data, appid):
        """
        Updates an existing record with the current data
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
            is_free = common.get_bool(common.get_from_json(data, "is_free"))

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
                coming_soon = not common.get_bool(release_date["coming_soon"])
                release_date = self.date_formatter.format_date(release_date["date"])
            else:
                coming_soon = False
                release_date = None

            stmt = "update games set " \
                   " name=?, type=?, required_age=?," \
                   " is_free=?, full_game_id=?, detailed_description=?," \
                   " about_the_game=?, short_description=?, price=?," \
                   " recommendations=?, is_released=?, release_date=?, screenshots=?," \
                   " movies=?, achievements=? where id=?"
            params = (game_name, type, required_age, is_free, full_game_id, detailed_description,
                      about_the_game, short_description, price, recommendations, coming_soon, release_date,
                      screenshots_num, movies_num, achievements, appid)
            c.execute(stmt, params)

            # Delete existing records to insert new ones instead
            tables = ["languages", "developers", "publishers", "platforms", "metacritic", "categories", "genres"]
            for table in tables:
                stmt = "delete from %s where gameid = ?" % table
                params = (appid,)
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

            self.printc("Record #" + str(appid) + " (" + game_name + ") updated.", common.Color.OKGREEN)

    def get_record(self, appid):
        appid = str(appid)
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
