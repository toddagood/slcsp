#!/usr/bin/env python3

import argparse
import os
import sys

from collections import defaultdict, namedtuple
from decimal import Decimal
from os.path import getmtime, isfile

class RateFinder(object):
    """A tool for finding the rate of the second lowest cost silver plan for a zipcode."""

    # Exceptions.
    class CsvError(Exception): pass

    # Define csv schemas.
    zips_schema = namedtuple('Zips', 'zipcode,state,county_code,name,rate_area')
    plans_schema = namedtuple('Plans', 'plan_id,state,metal_level,rate,rate_area')
    cache_schema = namedtuple('Cache', 'zipcode,slcsp_rate')

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
        # Process data from the zips_csv file.
        for data in self.read_csv(zips_csv, self.zips_schema):
            # Update the map.
            self.rate_areas[data.zipcode].add((data.state, data.rate_area))

    def read_plans_csv(self, plans_csv):
        """Reads a plans_csv file."""
        # Create a map from a rate area to a set of rates.
        self.rates = defaultdict(set)
        # Process data from the plans_csv file.
        for data in self.read_csv(plans_csv, self.plans_schema):
            if data.metal_level == 'Silver':
                # It is a silver plan, so update the map.
                self.rates[(data.state, data.rate_area)].add(Decimal(data.rate))

    def read_csv(self, csv, schema):
        """Reads a csv file, yielding data one line at a time."""
        # Get the header and field count from the schema.
        header = ','.join(schema._fields)
        cnt = len(schema._fields)
        # Open the csv file.
        with open(csv) as fp:
            # Read the first line.
            line = fp.readline()
            if line.rstrip('\n') != header:
                # The first line does not contain the expected header.
                raise self.CsvError('File {}: Line 1: Expected header: {}'.format(csv, header))
            # Read each data line.
            for i, line in enumerate(fp):
                # Strip the trailing newline character and split the line into fields based on commas.
                values = line.rstrip('\n').split(',')
                if len(values) != cnt:
                    # The number of fields in the data line does not match the number of fields in the header.
                    raise self.CsvError('File {}: Line {}: Expected {} columns but got {}'.format(csv, i+2, cnt, len(values)))
                # Yield the data using the schema.
                yield schema._make(values)

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
            rate_area = next(iter(rate_areas))
            # Get the rates for the rate area.
            rates = self.rates[rate_area]
            if len(rates) > 1:
                # There is an well defined second lowest rate for the zip code.
                rate = sorted(rates)[1]
                # Format the rate with two digits after the decimal point.
                rate = str(round(rate, 2))
        # Return the rate.
        return rate

    def dump_cache_csv(self, cache_csv):
        """Dumps a cache_csv for mapping zipcodes directly to slcsp rates."""
        # Get the header from the schema.
        header = ','.join(self.cache_schema._fields)
        # Write to the cache_csv file.
        with open(cache_csv, 'w') as fp:
            # Print the header.
            print(header, file=fp)
            # Consider every known zipcode.
            for zipcode in self.rate_areas.keys():
                # Get the rate.
                rate = self.find_rate(zipcode)
                if rate:
                    # The rate is known, so print a mapping.
                    print(zipcode, rate, sep=',', file=fp)

    def read_cache_csv(self, cache_csv):
        """Reads a cache_csv for mapping zipcodes directly to slcsp rates."""
        # Create a map from a zipcode to an slcsp_rate.
        self.cache = dict()
        # Process data from the cache_csv file.
        for data in self.read_csv(cache_csv, self.cache_schema):
            # Update the map.
            self.cache[data.zipcode] = data.slcsp_rate

class RateFinderCmd(RateFinder):
    """A command-line tool for determining the second lowest cost silver plan for a set of zipcodes."""

    # Exceptions.
    class UsageError(Exception): pass

    # Define csv schemas.
    in_schema = namedtuple('In', 'zipcode,rate')

    def __init__(self, args):
        """Initializes this RateFinderCmd."""
        # Construct an args parser and add args.
        parser = argparse.ArgumentParser(description='Finds the second lowest cost silver plan for a set of zipcodes.')
        parser.add_argument('-i', dest='in_csv', metavar='in_csv', required=True,
                            help='a csv file containing zipcodes to be processed')
        parser.add_argument('-z', dest='zips_csv', metavar='zips_csv', required=True,
                            help='a csv file that associates zipcode, state, and rate_area fields')
        parser.add_argument('-p', dest='plans_csv', metavar='plans_csv', required=True,
                            help='a csv file that associates state, rate_area, metal_level, and rate fields')
        parser.add_argument('-c', dest='cache_csv', metavar='cache_csv',
                            help='a csv file that associates zipcode and slcsp_rate fields')
        
        # Parse the command-line args.
        args = parser.parse_args(args)

        # Initialize this RateFinder.
        super().__init__(args.zips_csv, args.plans_csv, args.cache_csv)

        # Read the in_csv file and print results to stdout.
        self.read_in_csv(args.in_csv, sys.stdout)

    def read_in_csv(self, in_csv, out_fp):
        """Reads the in_csv file and prints results to an output file."""
        # Get the header from the schema.
        header = ','.join(self.in_schema._fields)
        # Print the header.
        print(header, file=out_fp)
        # Process data from the in_csv file.
        for data in self.read_csv(in_csv, self.in_schema):
            # Find the rate.
            rate = self.find_rate(data.zipcode)
            # Print the zipcode and rate.
            print(data.zipcode, rate, sep=',', file=out_fp)

if __name__ == '__main__':
    # Run the main program.
    try:
        RateFinderCmd(sys.argv[1:])
    except Exception as e:
        # Handle exceptions.
        if os.environ.get('SLCSP_DEV'):
            # Show tracebacks in development mode.
            raise e
        else:
            # Show formatted errors in production mode.
            print('Error: {}: {}'.format(type(e).__name__, e), file=sys.stderr)
            exit(1)
