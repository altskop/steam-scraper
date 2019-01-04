from datetime import datetime
import re


class DateFormatter:

    def __init__(self, target_format):
        self.target_format = target_format
        self.input_formats = []

    def add_input_format(self, input_format):
        self.input_formats.append(input_format)

    def set_input_formats(self, input_formats):
        self.input_formats = input_formats

    def format_date(self, entry):
        for format in self.input_formats:
            try:
                parsed_date = datetime.strptime(self.trim(entry), format)  # try to get the date
                formatted_date = parsed_date.strftime(self.target_format)
                return formatted_date
            except ValueError:
                pass  # if incorrect format, keep trying other formats
        return entry

    @staticmethod
    def trim(s):
        return re.sub(r'(\d)(st|nd|rd|th)', r'\1', s)
