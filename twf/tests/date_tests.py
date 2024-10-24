from django.test import TestCase

from twf.utils.date_utils import parse_date_string


class TestDateUtils(TestCase):
    """Test the tag_assigner function."""
    def test_date_parsing(self):

        test_data = [
            # date_str,           to_day       to_month       to_year
            ("1. Oktober 1945",   "1945-10-01", "1945-10",    "1945"),
            ("1945",              "1945-XX-XX", "1945-XX",    "1945"),
            ("Oktober 1945",      "1945-10-XX", "1945-10",    "1945"),
            ("12. Février 1766",  "1766-02-12", "1766-02",    "1766"),
            ("1st may 2020",      "2020-05-01", "2020-05",    "2020"),
            ("2nd of March 2020", "2020-03-02", "2020-03",    "2020"),
            ("22.12.1782",        "1782-12-22", "1782-12",    "1782"),
        ]

        for date_str, to_day, to_month, to_year in test_data:
            self.assertEqual(parse_date_string(date_str, "day"), to_day)
            self.assertEqual(parse_date_string(date_str, "month"), to_month)
            self.assertEqual(parse_date_string(date_str, "year"), to_year)