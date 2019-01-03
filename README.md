# Steam Apps Scraper

![python3.6](https://img.shields.io/badge/python-3.6-blue.svg) ![mit](https://img.shields.io/github/license/mashape/apistatus.svg)

Steam Apps Scraper is a configurable and fully automatic scraper designed to pull public data from Steam via its API or WebUI and store it in a SQLite database. It is primarily used to gather data on various apps released on Steam for the purpose of data analysis.

If you came here to get that data, but don't feel like waiting for 3-4 days for the scraper to work, you may get the latest database file [HERE](http://).


## Core Features:

- Utilizes both Steam API and Steam Web UI for data scraping
- Configurable via the [config file](config.yml)
- Automatic database integrity verification and creation
- Received data is automatically broken down and saved in a SQLite database
- Can be run in either verbose or silent mode

## Getting Started

### Prerequisites

The project requires **Python 3.6** to run, as well as the following packages:

- BeautifulSoup4
- requests
- urllib3

## Running the scraper

To run the script, execute the following command in the root directory of the project:
```
python3 main.py MODE [-v -f]
```
Where:
- MODE is the execution mode (can be one of the following: `all, games, tags, update`). Run with `-h` to get more information on execution modes.
- `-v or --verbose` will increase the verbosity of the script.
- `-f or --force` will force the script to go through the records that were marked as unreachable during previous runs. 

## Running the tests

If you have made any changes, you may want to run the existing unit tests to make sure nothing is broken. To do so, simply run `python3 unit_testing.py`.

Sample output:
```
....................
----------------------------------------------------------------------
Ran 24 tests in 11.485s

OK
```

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details