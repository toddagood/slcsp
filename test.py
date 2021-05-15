from nose import run
from slcsp import *
import unittest

class Test_Exceptions(unittest.TestCase):
    """Ensure exceptions are raised."""

    def test_zips_csv_not_found(self):
        """Ensure an exception is raised when the zips_csv file is not found."""
        with self.assertRaisesRegex(FileNotFoundError, 'not_zips.csv'):
            RateFinder('not_zips.csv', 'plans.csv')

    def test_plans_csv_not_found(self):
        """Ensure an exception is raised when the plans_csv file is not found."""
        with self.assertRaisesRegex(FileNotFoundError, 'not_plans.csv'):
            RateFinder('zips.csv', 'not_plans.csv')

    def test_zips_csv_empty(self):
        """Ensure an exception is raised when the zips_csv file is empty."""
        with self.assertRaisesRegex(RateFinder.CsvError, 'File .*empty.csv: Line 1: Expected header:'):
            RateFinder('test/empty.csv', 'plans.csv')

    def test_plans_csv_empty(self):
        """Ensure an exception is raised when the plans_csv file is empty."""
        with self.assertRaisesRegex(RateFinder.CsvError, 'File .*empty.csv: Line 1: Expected header:'):
            RateFinder('zips.csv', 'test/empty.csv')
        
    def test_zips_csv_extra_field(self):
        """Ensure an exception is raised when the zips_csv file has an extra field."""
        with self.assertRaisesRegex(RateFinder.CsvError, 'File .*zips_extra_field.csv: Line 4: Expected 5 columns but got 6'):
            RateFinder('test/zips_extra_field.csv', 'plans.csv')

    def test_plans_csv_extra_field(self):
        """Ensure an exception is raised when the plans_csv file has an extra field."""
        with self.assertRaisesRegex(RateFinder.CsvError, 'File .*plans_extra_field.csv: Line 4: Expected 5 columns but got 6'):
            RateFinder('zips.csv', 'test/plans_extra_field.csv')
        
    def test_zips_csv_missing_field(self):
        """Ensure an exception is raised when the zips_csv file has a missing field."""
        with self.assertRaisesRegex(RateFinder.CsvError, 'File .*zips_missing_field.csv: Line 4: Expected 5 columns but got 4'):
            RateFinder('test/zips_missing_field.csv', 'plans.csv')

    def test_plans_csv_missing_field(self):
        """Ensure an exception is raised when the plans_csv file has a missing field."""
        with self.assertRaisesRegex(RateFinder.CsvError, 'File .*plans_missing_field.csv: Line 4: Expected 5 columns but got 4'):
            RateFinder('zips.csv', 'test/plans_missing_field.csv')

class Test_Mappings(unittest.TestCase):
    """Ensure mappings are correct."""

    def setUp(self):
        """Constructs a RateFinder."""
        self.rate_finder = RateFinder('zips.csv', 'plans.csv')
        
    def test_rate_found_64148(self):
        """Ensure the correct rate is found for zipcode 64148."""
        self.assertEqual(self.rate_finder.find_rate('64148'),
                         '245.20')

    def test_rate_areas_64148(self):
        """Ensure that zipcode 64148 only maps to a single rate area ('MO', '3')."""
        self.assertEqual(sorted(self.rate_finder.rate_areas['64148']),
                         [('MO', '3')])

    def test_rates_MO_3(self):
        """Ensure that rate area ('MO', '3') has multiple rates, and the second lowest rate was found."""
        self.assertEqual(', '.join(map(str, sorted(self.rate_finder.rates[('MO', '3')]))),
                         '234.6, 245.2, 251.08, 253.65, 265.25, 265.82, 271.64, 290.05, 298.87, 312.06, 319.57, 341.24, 351.6')

    def test_rate_not_found_40813(self):
        """Ensure a rate is not found for zipcode 40813."""
        self.assertEqual(self.rate_finder.find_rate('40813'),
                         '')

    def test_rate_areas_40813(self):
        """Ensure that zipcode 40813 only maps to a single rate area ('KY', '8'), so that wasn't the problem."""
        self.assertEqual(sorted(self.rate_finder.rate_areas['40813']),
                         [('KY', '8')])

    def test_rates_KY_8(self):
        """Ensure that rate area ('KY', '8') has no silver plans, so that was the problem."""
        self.assertEqual(sorted(self.rate_finder.rates[('KY', '8')]),
                         [])

    def test_rate_not_found_46706(self):
        """Ensure a rate is not found for zipcode 46706."""
        self.assertEqual(self.rate_finder.find_rate('46706'),
                         '')

    def test_rate_areas_46706(self):
        """Ensure that zipcode 46706 maps to two rate areas, so that was the problem."""
        self.assertEqual(sorted(self.rate_finder.rate_areas['46706']),
                         [('IN', '3'), ('IN', '4')])

    def test_rates_IN_3(self):
        """Ensure that rate area ('IN', '3') has a second lowest silver rate, so that wasn't the problem."""
        self.assertEqual(', '.join(map(str, sorted(self.rate_finder.rates[('IN', '3')])[:3])),
                         '277.56, 282.43, 289.6')
        
    def test_rates_IN_4(self):
        """Ensure that rate area ('IN', '4') has a second lowest silver rate, so that wasn't the problem."""
        self.assertEqual(', '.join(map(str, sorted(self.rate_finder.rates[('IN', '4')])[:3])),
                         '268.1, 272.81, 279.73')
        
    def test_rate_not_found_07734(self):
        """Ensure a rate is not found for zipcode 07734."""
        self.assertEqual(self.rate_finder.find_rate('07734'),
                         '')

    def test_rate_areas_07734(self):
        """Ensure that zipcode 07734 only maps to a single rate area ('NJ', '1'), so that wasn't the problem."""
        self.assertEqual(sorted(self.rate_finder.rate_areas['07734']),
                         [('NJ', '1')])

    def test_rates_NJ_1(self):
        """Ensure that rate area ('NJ', '1') only has a single rate, so that was the problem."""
        self.assertEqual(', '.join(map(str, sorted(self.rate_finder.rates[('NJ', '1')]))),
                         '262.65')

    def test_rate_found_26716(self):
        """Ensure the correct rate is found for zipcode 26716."""
        self.assertEqual(self.rate_finder.find_rate('26716'),
                         '291.76')

    def test_rate_areas_26716(self):
        """Ensure that zipcode 26716, which straddles two counties, maps to a single rate area ('WV', '9')."""
        self.assertEqual(sorted(self.rate_finder.rate_areas['26716']),
                         [('WV', '9')])

    def test_rates_WV_9(self):
        """Ensure that the third rate is used when the first two lowest cost silver plans have the same rate."""
        # ('WV', '9') has the following silver rates ['278.9', '278.9', '291.76', '295.05', '295.63']
        # The rate must be greater than the lowest rate.
        self.assertEqual(', '.join(map(str, sorted(self.rate_finder.rates[('WV', '9')]))),
                         '278.9, 291.76, 295.05, 295.63')

if __name__ == '__main__':
    run()
