"""verbnetparser.py

Adaptation of the VerbNet xml parser, loads PropBank instead. This is designed to have as close to the same functionality
so that programs can work with either resource as necessary
"""

import os
import bs4
import re
import json
import config
import verbnet

VN_RE = r"([1-9][0-9]?[0-9]?([.-][0-9]+)+)"

class PropBankParser(object):
    """Parse PropBank XML files, and turn them into a list of BeautifulSoup
    objects"""

    def __init__(self, directory=None, version="unified"):
        PROPBANK_PATH = directory
        fnames = [f for f in os.listdir(PROPBANK_PATH) if f.endswith(".xml")]
        self.filenames = [os.path.join(PROPBANK_PATH, fname) for fname in fnames]
        self.version = version
        self.vn2pb = json.load(open(config.EXTERNAL_VN2PB_PATH))
        self.pb2vn = {}
        for key in self.vn2pb:
            for value in self.vn2pb[key]:
                if value not in self.pb2vn:
                    self.pb2vn[value] = []
                self.pb2vn[value].append(key)

        self.parsed_files = self.parse_files()
        self.frame_dict = {}
        self.rolesets = {}

        for parse in self.parsed_files:
            for roleset in parse.findAll("roleset"):
                pb_roleset = PropBankRoleset(roleset, version)
                self.rolesets[pb_roleset.ID] = pb_roleset

    def parse_files(self):
        """Parse a list of XML files using BeautifulSoup. Returns list of parsed
        soup objects"""
        parsed_files = []
        for fname in self.filenames:
            parsed_files.append(bs4.BeautifulSoup(open(fname, encoding="utf-8"), "lxml-xml"))
        return parsed_files

    def get_pb_vn_mappings(self, verbnet):
        vn_members = [member.name for member in verbnet.get_members()]
        res = {}
        for roleset in self.rolesets:
#            print (self.rolesets[roleset].role_mappings)
            if not self.rolesets[roleset].vnc:
                if roleset in self.pb2vn:
                    print("roleset found in mapping file;;" + roleset + str(self.pb2vn[roleset]))
                    self.rolesets[roleset].vnc = ["-".join(vnc.split("-")[1:]) for vnc in self.pb2vn[roleset]]
                elif roleset.split(".")[0] in vn_members:
                    print ("no vn mapping, but it's in verbnet;;" + roleset)
            for vnc in self.rolesets[roleset].vnc:
                new_c = verbnet.find_correct_subclass(vnc, roleset.split(".")[0])
                if not new_c:
                    print ("class not found;;" + roleset + ";;" + vnc)
                elif new_c == vnc:
                    res[roleset] = {"vn_class":vnc}
                    print ("class is good;;" + roleset + ";;" + vnc)
                else:
                    res[roleset] = {"vn_class":vnc}
                    print ("class/member found, update;;" + roleset + ";;" + vnc + ";;" + new_c)
                if roleset in res:
                    for arg in self.rolesets[roleset].role_mappings:
                        if res[roleset]["vn_class"] in self.rolesets[roleset].role_mappings[arg]:
                            res[roleset][arg] = self.rolesets[roleset].role_mappings[arg][res[roleset]["vn_class"]]
        return res


    def write_pb_vn_mappings(self, verbnet):
        mapping_dict = self.get_pb_vn_mappings(verbnet)
        print (mapping_dict)

class AbstractXML(object):
    """Abstract class to be inherited by other classes that share the same
    features"""

    def __init__(self, soup):
        self.soup = soup

    def get_category(self, cat, special_soup=None):
        """Extracts the category from a soup, with the option to specify a soup.

        For MEMBERs, we have:
        name (lexeme),
        wn (WordNet category)
        grouping (PropBank grouping)"""
        if not special_soup:
            special_soup = self.soup
        try:
            return special_soup.get(cat)
        except AttributeError:
            return []


class PropBankRoleset(AbstractXML):
    def __init__(self, soup, version="unified"):
        super().__init__(soup)
        self.ID = self.get_category("id", self.soup)
        self.name, self.framenet, self.vnc = None, [], []
        self.role_mappings = self.populate_role_mappings()

        if version == "unified":
            self.name = self.get_category("name", self.soup)
            alias = self.soup.find_all("alias")
            self.framenet = self.get_category("framenet", alias)
            self.vnc = self.get_category("verbnet", alias)
            if not self.vnc:
                self.parse_extra_vnc()
        else:
            try:
                self.name = self.get_category("name", self.soup)
            except IndexError as e:
                pass
            try:
                self.framenet = self.get_category("framnet", self.soup)
                self.vnc = self.get_category("vncls", self.soup)
            except AttributeError as e:
                pass

    def __repr__(self):
        return str([self.ID, self.framenet, self.vnc, self.name])

    def populate_role_mappings(self):
        rms = {}
        for role in self.soup.find_all("role"):
            role_number = "ARG" + self.get_category("n", role)
            rms[role_number] = {}
            for vn_role in role.find_all("vnrole"):
                vntheta = self.get_category("vntheta", vn_role).lower()
                vncls = self.get_category("vncls", vn_role)
                rms[role_number][vncls] = vntheta
        return rms


    def parse_extra_vnc(self):
        """
        Accounts for cases where the PB file doesn't explicitly map to VN, but the class is in the roles or the notes
        """
        try:
            vnc_cands = set()
            for note in self.soup.find_all("note"):
                vnc_cands.update([g[0] for g in re.findall(VN_RE, note.text)])
            for vnrole in self.soup.find_all("vnrole"):
                vnc_cands.add(vnrole.get("vncls"))
            self.vnc = vnc_cands
        except IndexError:
            return


if __name__ == "__main__":
    vn = verbnet.VerbNetParser(directory=config.VN_RESOURCE_PATH)
    pb = PropBankParser(directory=config.PB_RESOURCE_PATH)

    res = pb.get_pb_vn_mappings(vn)
    #for r in res:
    #    print (r, res[r])
    json.dump(res, open("../instances/pb-vn2.json", "w"))