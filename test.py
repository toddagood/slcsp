from nose import run
from nose.tools import raises, eq_
from slcsp import *

@raises(FileNotFoundError)
def test_zips_csv_not_found():
    RateFinder('not_zips.csv', 'plans.csv')

@raises(FileNotFoundError)
def test_plans_csv_not_found():
    RateFinder('zips.csv', 'not_plans.csv')

@raises(RateFinder.CsvError)
def test_zips_csv_empty():
    RateFinder('test/empty.csv', 'plans.csv')

@raises(RateFinder.CsvError)
def test_plans_csv_empty():
    RateFinder('zips.csv', 'test/empty.csv')
    
@raises(RateFinder.CsvError)
def test_zips_csv_extra_field():
    RateFinder('test/zips_extra_field.csv', 'plans.csv')

@raises(RateFinder.CsvError)
def test_plans_csv_extra_field():
    RateFinder('zips.csv', 'test/plans_extra_field.csv')
    
@raises(RateFinder.CsvError)
def test_zips_csv_missing_field():
    RateFinder('test/zips_missing_field.csv', 'plans.csv')

@raises(RateFinder.CsvError)
def test_plans_csv_missing_field():
    RateFinder('zips.csv', 'test/plans_missing_field.csv')

def test_rate_found_64148():
    rate_finder = RateFinder('zips.csv', 'plans.csv')
    eq_(rate_finder.find_rate('64148'), '245.20')

def test_rate_areas_64148():
    rate_finder = RateFinder('zips.csv', 'plans.csv')
    eq_(sorted(rate_finder.rate_areas['64148']), [('MO', '3')])

def test_rates_MO_3():
    rate_finder = RateFinder('zips.csv', 'plans.csv')
    eq_(', '.join(map(str, sorted(rate_finder.rates[('MO', '3')]))), '234.6, 245.2, 251.08, 253.65, 265.25, 265.82, 271.64, 290.05, 298.87, 312.06, 319.57, 341.24, 351.6')

def test_rate_not_found_40813():
    rate_finder = RateFinder('zips.csv', 'plans.csv')
    eq_(rate_finder.find_rate('40813'), '')

def test_rate_areas_40813():
    rate_finder = RateFinder('zips.csv', 'plans.csv')
    eq_(sorted(rate_finder.rate_areas['40813']), [('KY', '8')])

def test_rates_KY_8():
    rate_finder = RateFinder('zips.csv', 'plans.csv')
    eq_(sorted(rate_finder.rates[('KY', '8')]), [])

def test_rate_not_found_46706():
    rate_finder = RateFinder('zips.csv', 'plans.csv')
    eq_(rate_finder.find_rate('46706'), '')

def test_rate_areas_46706():
    rate_finder = RateFinder('zips.csv', 'plans.csv')
    eq_(sorted(rate_finder.rate_areas['46706']), [('IN', '3'), ('IN', '4')])

def test_rates_IN_3():
    rate_finder = RateFinder('zips.csv', 'plans.csv')
    eq_(', '.join(map(str, sorted(rate_finder.rates[('IN', '3')])[:3])), '277.56, 282.43, 289.6')
    
def test_rates_IN_4():
    rate_finder = RateFinder('zips.csv', 'plans.csv')
    eq_(', '.join(map(str, sorted(rate_finder.rates[('IN', '4')])[:3])), '268.1, 272.81, 279.73')
    
if __name__ == '__main__':
    run()
