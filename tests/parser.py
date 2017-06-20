#!/usr/bin/env python3
import argparse
from asciitree import LeftAligned
from collections import OrderedDict as OD
from fuzzywuzzy import fuzz

from gedcom import Gedcom


class Formatter:
    """Format information into a pretty, standard way."""
    def __init__(self):
        pass

    def individual(self, individual, depth=1):
        """Format an individual."""

        """
        tree = {
            'asciitree': OD([
                ('sometimes',
                    {'you': {}}),
                ('just',
                    {'want': OD([
                        ('to', {}),
                        ('draw', {}),
                    ])}),
                ('trees', {}),
                ('in', {
                    'your': {
                        'terminal': {}
                    }
                })
            ])
        }
        """
        tree = {
            'me': OD(
                ''
            )
        }

        tr = LeftAligned()
        return tr(tree)


class Anomaly:
    """An anomaly in a genealogy tree.

    An anomaly is something we've found in a genealogy tree that looks
    like it's incorrect. This could be something like variant spellings of
    a name, duplicate names within a branch, etc.
    """
    def __init__(self, individual, anomaly):
        self.individual = individual
        self.anomaly = anomaly

    def __str__(self):
        return "Unimplemented"



class AnomalySurname(Anomaly):
    def __str__(self):
        return "Anomaly detected: {}".format(self.anomaly)


class Oracle:
    def __init__(self, filename):
        self.gedcom = Gedcom(filename)

    def analyze(self):
        """Analyze the gedcom tree and report potential issues."""
        anomalies = []

        return anomalies

    def analyze_fraternal_surnames(self, individual):
        """Analyze the male line to check for incorrect surnames."""

        anomalies = []
        surname = individual.name()[1]

        ancestors = self.find_paternal_ancestors(individual)
        for ancestor in ancestors:
            (first, last) = ancestor.name()

            # Find all ancestors with a name close to the home user
            if fuzz.ratio(individual.name()[1], last) >= 75:
                if surname.upper() != last.upper():
                    anomalies.append(AnomalySurname(
                        individual,
                        "Surname variation: {} vs. {}".format(
                            surname, last
                        )
                    ))
                print(last)

        return anomalies

    def find_home_individual(self):
        """Attempt to identify the home individual of this tree."""
        for element in self.gedcom.element_list():
            if element.is_individual():
                return element
        return None

    def find_ancestor_by_gender(self, individual, gender):
        """Gender should be M or F"""
        ancestors = []
        parents = self.gedcom.get_parents(individual)
        for parent in parents:
            if parent.gender() == gender:
                ancestors.append(parent)
            # Recursion is fun!
            ancestors.extend(self.find_ancestor_by_gender(parent, gender))
        return ancestors

    def find_maternal_ancestors(self, individual):
        """Get all of an individual's maternal ancestors."""
        return self.find_ancestor_by_gender(individual, 'F')

    def find_paternal_ancestors(self, individual):
        """Get all of an individual's paternal ancestors."""
        return self.find_ancestor_by_gender(individual, 'M')

    def find_individual(self, criteria):
        """ Check in this element matches all of the given criteria.

        The criteria is a colon-separated list, where each item in the
        list has the form [name]=[value]. The following criteria are supported:
        surname=[name]
             Match a person with [name] in any part of the surname.
        name=[name]
             Match a person with [name] in any part of the given name.
        birth=[year]
             Match a person whose birth year is a four-digit [year].
        birthrange=[year1-year2]
             Match a person whose birth year is in the range of years from
             [year1] to [year2], including both [year1] and [year2].
        death=[year]
        deathrange=[year1-year2]
        """

        for element in self.gedcom.element_list():
            if element.criteria_match(criteria):
                return element
        pass


def get_argparser():
    parser = argparse.ArgumentParser(description='Do genealogy!')

    parser.add_argument('-g', '--gedcom', help='Path to your gedcom file')
    return parser


def main():
    parser = get_argparser()
    args = parser.parse_args()
    if args.gedcom:
        o = Oracle(args.gedcom)

        me = o.find_home_individual()
        if me:
            print(me.name())
            anomalies = o.analyze_fraternal_surnames(me)
            for anomaly in anomalies:
                print(anomaly)
                #  print("Anomaly detected: {}".format(anomaly.anomaly))
            # ancestors = o.find_fraternal_ancestors(me)
            # for ancestor in ancestors:
            #     print(ancestor.name())
            #     # print(ancestor)

    else:
        parser.print_help()
    pass


if __name__ == "__main__":
    main()
