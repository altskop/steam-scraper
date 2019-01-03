import sqlite3
from . import common


class DBHandler:
    def __init__(self, db_file):
        self.db_file = db_file
        self.initialize_db()

    def initialize_db(self):
        # Connect to database. If the file doesn't exist, create it
        conn = sqlite3.connect(self.db_file)
        with conn:
            c = conn.cursor()
            try:
                self.table_verification(c)
            except sqlite3.OperationalError:
                # If the tables don't exist, create them
                print("Database failed verification. Do you want to create a new database?")
                common.printcolor("WARNING: If a database already exists, it will be completely destroyed "
                                  "and existing data will be lost.", common.Color.WARNING)
                choice = input("Type in \"yes\" if you want to create a new database.")
                if choice.lower() == "yes":
                    self.create_tables(c)
                    print("Database successfully recreated.")
                else:
                    print("Exiting...")
                    exit(0)

    @staticmethod
    def table_verification(cursor):
        c = cursor
        print("Verifying integrity of the database...")
        c.execute("select id, name, type, required_age, is_free, full_game_id, detailed_description,"
                  "about_the_game, short_description, price, rating, recommendations, release_date, screenshots,"
                  "movies, achievements from games;")
        c.execute("select name, gameid from tags;")
        c.execute("select name, gameid from languages;")
        c.execute("select name, gameid from developers;")
        c.execute("select name, gameid from publishers;")
        c.execute("select score, url, gameid from metacritic;")
        c.execute("select name, gameid from categories;")
        c.execute("select name, gameid from genres;")
        c.execute("select name, status, gameid from platforms;")
        c.execute("select id from inaccessible;")
        print("Database passed verification.")
        return True

    @staticmethod
    def create_tables(cursor):
        c = cursor
        query = """
                drop table if exists games;
                drop table if exists languages;
                drop table if exists developers;
                drop table if exists publishers;
                drop table if exists metacritic;
                drop table if exists categories;
                drop table if exists genres;
                drop table if exists platforms;
                drop table if exists tags;
                drop table if exists inaccessible;
                CREATE TABLE games(
                id integer primary key not null,
                name varchar(200) not null,
                type varchar(50),
                required_age integer,
                is_free boolean,
                full_game_id integer,
                detailed_description text,
                about_the_game text,
                short_description text,
                price integer,
                rating tinyint,
                recommendations integer,
                is_released boolean,
                release_date datetime,
                screenshots integer,
                movies integer,
                achievements integer);
                CREATE TABLE languages(name varchar(40), gameid integer, FOREIGN KEY(gameid) REFERENCES games(id));
                CREATE TABLE developers(name varchar(60), gameid integer, FOREIGN KEY(gameid) REFERENCES games(id));
                CREATE TABLE publishers(name varchar(60), gameid integer, FOREIGN KEY(gameid) REFERENCES games(id));
                CREATE TABLE metacritic(score integer, url text, gameid integer, FOREIGN KEY(gameid) REFERENCES games(id));
                CREATE TABLE categories(name varchar(120), gameid integer, FOREIGN KEY(gameid) REFERENCES games(id));
                CREATE TABLE genres(name varchar(120), gameid integer, FOREIGN KEY(gameid) REFERENCES games(id));
                CREATE TABLE platforms(name varchar(30), status boolean, gameid integer, FOREIGN KEY(gameid) REFERENCES games(id));
                CREATE TABLE tags(name varchar(120), gameid integer, FOREIGN KEY(gameid) REFERENCES games(id));
                CREATE TABLE inaccessible(id integer primary key not null);
                """
        c.executescript(query)


