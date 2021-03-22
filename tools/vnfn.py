from nltk.corpus import framenet
from lxml import etree
import datetime
import json

import verbnet
import config

VN_LOC = config.VN_RESOURCE_PATH

vn = verbnet.VerbNetParser(directory=VN_LOC)
possible_classes = {"-".join(c.split("-")[1:]): [m.name for m in vn.verb_classes_dict[c].members] for c in
                    vn.verb_classes_dict}

possible_frames = {}
for lu in framenet.lus():
    if lu.frame.name not in possible_frames:
        possible_frames[lu.frame.name] = [lu.lexemes[0].name]
    else:
        possible_frames[lu.frame.name].append(lu.lexemes[0].name)


class Mapping():
    def __init__(self, member, vn_class, fn_frame):
        self.member = member
        self.vn_class = vn_class
        self.fn_frame = fn_frame
        self.errors = self.verify()

    def __str__(self):
        return self.member + " " + self.vn_class + " " + self.fn_frame

    def __eq__(self, other):
        return self.member == other.member and self.vn_class == other.vn_class and self.fn_frame == other.fn_frame

    def __lt__(self, other):
        if self.vn_class == other.vn_class:
            return self.member < other.member
        return self.vn_class < other.vn_class

    def __gt__(self, other):
        if self.vn_class == other.vn_class:
            return self.member > other.member
        return self.vn_class > other.vn_class

    def __hash__(self):
        return hash(self.member) * hash(self.vn_class) * hash(self.fn_frame)

    def as_xml(self):
        out_node = etree.Element("vncls", attrib={"class":self.vn_class, "fnframe":self.fn_frame, "vnmember":self.member})
        return out_node

    def verify(self):
        res = []
        if self.vn_class not in possible_classes.keys():
            res.append("class doesn't exits")
        elif self.member not in possible_classes[self.vn_class]:
            res.append("verb not in class")
        if self.fn_frame not in possible_frames.keys():
            res.append("frame doesn't exist")
        elif self.member not in possible_frames[self.fn_frame]:
            res.append("verb not in frame")
        return res


class ElementMapping(Mapping):
    def __init__(self, element):
        super().__init__("", element.attrib["class"], element.attrib["fnframe"])
        self.role_dict = {}

        for role in element.getchildren()[0].getchildren():
            self.role_dict[role.attrib["vnrole"].lower()] = role.attrib["fnrole"]


def load_mappings(mapping_file, as_dict=True):
    mappings = set()
    tree = etree.parse(open(mapping_file, encoding="utf-8"))
    root = tree.getroot()

    for e in root:
        mappings.add(Mapping(e.attrib["vnmember"], e.attrib["class"], e.attrib["fnframe"]))

    if as_dict:
        d = {}
        for m in mappings:
            k = m.vn_class + "-" + m.member
            if k not in d:
                d[k] = []
            d[k].append(m.fn_frame)
        return d
    return mappings


def load_element_mappings(mapping_file, to_dict=True):
    mappings = set()
    tree = etree.parse(open(mapping_file, encoding="utf-8"))
    root = tree.getroot()

    for e in root:
        mappings.add(ElementMapping(e))

    if to_dict:
        d = {}
        for m in mappings:
            k = m.vn_class + ";" + m.fn_frame
            d[k] = m.role_dict
        return d

    return mappings


def write_mappings(mappings, output_file, version="sl2", out_format="json"):
    if out_format == "json":
        json.dump(mappings, open(output_file, "w"))
    else:
        root = etree.Element('verbnet-framenet_MappingData', attrib={"date": str(datetime.datetime.now()), "versionID":version})

        for m in sorted(list(mappings)):
            print (m)
            root.append(m.as_xml())
        out_str = etree.tostring(root, pretty_print=True)
        with open(output_file, 'wb') as output:
            output.write(out_str)


def combine_old_and_fixed(output_file):
    old_maps = load_mappings(config.OLD_VN2FN_PATH)
    new_maps = load_mappings(config.FIXED_VN2FN_PATH)
    old_maps = {m for m in old_maps if not m.errors}
    for m in new_maps:
        if m in old_maps:
            old_maps.remove(m)
        old_maps.add(m)
    write_mappings(old_maps, output_file)


def test():
    m = load_mappings(config.VN2FN_PATH, as_dict=True)
    write_mappings(m, "../instances/vn-fn2.json", "json")

if __name__ == "__main__":
    test()