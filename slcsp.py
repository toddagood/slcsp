#!/usr/bin/env python3

from collections import defaultdict
from os import environ
from os.path import getmtime, isfile
from sys import argv, stdout, stderr

class RateFinder(object):
    """A tool for finding the rate of the second lowest cost silver plan for a zipcode."""

    # Exceptions.
    class CsvError(Exception): pass

    def __init__(self, zips_csv, plans_csv, cache_csv=None):
        """Initializes this RateFinder."""
        # Disable cached mapping.
        self.use_cache = False
        if cache_csv:
            # Will use caching.
            if (isfile(cache_csv) and isfile(zips_csv) and isfile(plans_csv)
                and getmtime(cache_csv) > getmtime(zips_csv)
                and getmtime(cache_csv) > getmtime(plans_csv)):
                # The cache_csv file is available and up-to-date, so use it.
                pass
            else:
                # The cache_csv file does not exist or is out-of-date.
                # Create/update it.
                # Read the zips_csv file.
                self.read_zips_csv(zips_csv)
                # Read the plans_csv file.
                self.read_plans_csv(plans_csv)
                # Dump the cache_csv file.
                self.dump_cache_csv(cache_csv)

            # Read the cache_csv file.
            self.read_cache_csv(cache_csv)
            # Enable cached mapping.
            self.use_cache = True
        else:
            # Will not use caching.
            # Read the zips_csv file.
            self.read_zips_csv(zips_csv)
            # Read the plans_csv file.
            self.read_plans_csv(plans_csv)

    def read_zips_csv(self, zips_csv):
        """Reads a zips_csv file."""
        # Create a map from a zipcode to a set of rate areas.
        self.rate_areas = defaultdict(set)
        # Define the expected header of the zips_csv file.
        header = 'zipcode,state,county_code,name,rate_area'
        # Process data from the zips_csv file.
        for data in self.read_csv(zips_csv, header):
            # Unpack the data.
            zipcode, state, _, _, rate_area = data
            # Update the map.
            self.rate_areas[zipcode].add((state, rate_area))

    def read_plans_csv(self, plans_csv):
        """Reads a plans_csv file."""
        # Create a map from a rate area to a set of rates.
        self.rates = defaultdict(set)
        # Define the expected header of the plans_csv file.
        header = 'plan_id,state,metal_level,rate,rate_area'
        # Process data from the plans_csv file.
        for data in self.read_csv(plans_csv, header):
            # Unpack the data.
            _, state, metal_level, rate, rate_area = data
            if metal_level == 'Silver':
                # It is a silver plan, so update the map.
                self.rates[(state, rate_area)].add(float(rate))

    def read_csv(self, csv, header):
        """Reads a csv file, yielding data one line at a time."""
        # Count the number of fields in the expected header.
        cnt = len(header.split(','))
        # Open the csv file.
        fp = open(csv)
        # Read the first line.
        line = fp.readline()
        if line.rstrip('\n') != header:
            # The first line does not contain the expected header.
            raise self.CsvError('File {}: Line 1: Expected header: {}'.format(csv, header))
        # Read each data line.
        for i, line in enumerate(fp):
            # Strip the trailing newline character and split the line into fields based on commas.
            data = line.rstrip('\n').split(',')
            if len(data) != cnt:
                # The number of fields in the data line does not match the number of fields in the header.
                raise self.CsvError('File {}: Line {}: Expected {} columns but got {}'.format(csv, i+2, cnt, len(data)))
            # Yield the data.
            yield data
        # Close the file.
        fp.close()

    def find_rate(self, zipcode):
        """Returns a string representing the rate for a zipcode, or an empty string if the rate is unknown or ambiguous."""
        if self.use_cache:
            # Use the cached mapping.
            return self.cache.get(zipcode, '')
        # Determine the rate. Initially the rate is unknown.
        rate = ''
        # Get the rate areas for the zipcode.
        rate_areas = self.rate_areas[zipcode]
        if len(rate_areas) == 1:
            # Get the rate area (there is exactly one, so there is no ambiguity).
            rate_area = rate_areas.pop()
            # Get the rates for the rate area.
            rates = self.rates[rate_area]
            if len(rates) > 1:
                # There is an well defined second lowest rate for the zip code.
                rate = sorted(rates)[1]
                # Format the rate with two digits after the decimal point.
                rate = '%.2f' % (rate, )
        # Return the rate.
        return rate

    def dump_cache_csv(self, cache_csv):
        """Dumps a cache_csv for mapping zipcodes directly to slcsp rates."""
        with open(cache_csv, 'w') as fp:
            print('zipcode', 'slcsp_rate', sep=',', file=fp)
            for zipcode in self.rate_areas.keys():
                rate = self.find_rate(zipcode)
                if rate:
                    print(zipcode, rate, sep=',', file=fp)

    def read_cache_csv(self, cache_csv):
        """Reads a cache_csv for mapping zipcodes directly to slcsp rates."""
        # Create a map from a zipcode to an slcsp_rate.
        self.cache = dict()
        # Define the expected header of the cache_csv file.
        header = 'zipcode,slcsp_rate'
        # Process data from the cache_csv file.
        for data in self.read_csv(cache_csv, header):
            # Unpack the data.
            zipcode, slcsp_rate = data
            # Update the map.
            self.cache[zipcode] = slcsp_rate

class RateFinderCmd(RateFinder):
    """A command-line tool for determining the second lowest cost silver plan for a set of zipcodes."""

    # Exceptions.
    class UsageError(Exception): pass

    def __init__(self):
        """Initializes this RateFinderCmd."""
        if len(argv) != 4:
            # Required args are missing.
            raise self.UsageError("""

Usage: {} <in.csv> <zips.csv> <plans.csv>

Reads zipcodes from <in.csv> which must contain two columns (zipcode,rate).
Prints the same CSV file to stdout, but with the rate information replaced
with the second lowest cost silver plan for that zip code.

Data for mapping zipcodes to region codes is loaded from <zips.csv>.

Data for mapping region codes to plans and their corresponding rates
is loaded from <plans.csv>.

""".format(argv[0]))

        # Unpack the args.
        _, in_csv, zips_csv, plans_csv = argv

        # Initialize this RateFinder.
        super().__init__(zips_csv, plans_csv, 'cache.csv')

        # Read the in_csv file and output results to stdout.
        self.read_in_csv(in_csv, stdout)

    def read_in_csv(self, in_csv, out_fp):
        """Reads the in_csv file and output results to stdout."""
        # Define the expected header of the in_csv file.
        header = 'zipcode,rate'
        # Print the header.
        print(header, file=out_fp)
        # Process data from the in_csv file.
        for data in self.read_csv(csv=in_csv, header=header):
            # Unpack the data.
            zipcode, _ = data
            # Find the rate.
            rate = self.find_rate(zipcode)
            # Print the zipcode and rate.
            print(zipcode, rate, sep=',', file=out_fp)

if __name__ == '__main__':
    # Run the main program.
    try:
        RateFinderCmd()
    except Exception as e:
        # Handle exceptions.
        if environ.get('SLCSP_DEV'):
            # Show tracebacks in development mode.
            raise e
        else:
            # Show formatted errors in production mode.
            print('Error: {}: {}'.format(type(e).__name__, e), file=stderr)
            exit(1)
