"""ontonotes.py

Adaptation of the VerbNet xml parser, loads Ontonotes instead. This is designed to have as close to the same functionality
so that programs can work with either resource as necessary
"""

import os
import bs4

VN_RE = r"([1-9][0-9]?[0-9]?([.-][0-9]+)+)"

class OntoNotesParser(object):
    """Parse OntoNotes Sense grouping XML files, and turn them into a list of BeautifulSoup
    objects"""

    def __init__(self, directory=None):
        """Take all verbnet files, if max_count is used then take the first max_count
        files, if file_list is used, read the filenames from the file."""
        GROUPING_PATH = directory
        fnames = [f for f in os.listdir(GROUPING_PATH) if f.endswith(".xml")]
        self.filenames = [os.path.join(GROUPING_PATH, fname) for fname in fnames]
        self.parsed_files = self.parse_files()
        self.frame_dict = {}
        self.groupings = {}

        for parse in self.parsed_files:
            for sense in parse.findAll("sense"):
                on_sense = SenseGrouping(sense, parse.find("inventory").get("lemma"))
                self.groupings[on_sense.ID] = on_sense


    def parse_files(self):
        """Parse a list of XML files using BeautifulSoup. Returns list of parsed
        soup objects"""
        parsed_files = []
        for fname in self.filenames:
            parsed_files.append(bs4.BeautifulSoup(open(fname, encoding="utf-8"), "lxml-xml"))
        return parsed_files

class SenseGrouping():
    def __init__(self, soup, file_lemma):
        self.lemma = file_lemma
        self.n = soup.get("n")
        self.group = soup.get("group")
        self.name = soup.get("name")

        mappings = soup.find("mappings")
        self.pb_mappings, self.vn_mappings, self.fn_mappings = None, None, None
        if mappings.find("pb"):
            self.pb_mappings = mappings.find("pb").text.split(",")
        if mappings.find("vn"):
            self.vn_mappings = mappings.find("vn").text.split(",")
        if mappings.find("fn"):
            self.fn_mappings = mappings.find("fn").text.split(",")

        self.ID = file_lemma + "-" + soup.get("n")
