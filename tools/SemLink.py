import sys
import os

from nltk.corpus import framenet

import verbnet
import propbank
import ontonotes
import annotation
import vnfn

import json

import logging
logging.basicConfig(filename='semlink.log',level=logging.DEBUG)

data_root = "put the location of your resources here"

PB_RELEASE = data_root + "propbank-release-master/data/ontonotes/nw/wsj/"
ON_RELEASE = data_root + "wsj_on/"
VN_ANNS = data_root + "annotations/"

def normalize_vnc(vnc):
    return "-".join(vnc.split("-")[1:])

class SemLink(object):
    def __init__(self, filename, version):
        self.annotations = {}
        self.version = version

        for line in open(filename).readlines():
            ann = annotation.SemLinkAnnotation(line)
            self.annotations[ann.instance] = ann

        self.vno, self.pbo, self.ono, self.fno, self.vn_pb_jsono, self.vn_fno, self.vn_fn_roleso = None, None, None, None, None, None, None

    def vn(self, version="3.3"):
        if not self.vno:
            self.vno = verbnet.VerbNetParser(version=version)
        return self.vno

    def fn(self):
        if not self.fno:
            self.fno = framenet
        return self.fno

    def pb(self, directory="C:/Users/Kevin/PycharmProjects/propbank-frames/frames/", version="unified"):
        if not self.pbo:
            self.pbo = propbank.PropBankParser(directory=directory, version=version)
        return self.pbo

    def on(self, directory="C:/Users/Kevin/PycharmProjects/lexical_resources/sense-inventories"):
        if not self.ono:
            self.ono = ontonotes.OntoNotesParser(directory=directory)
        return self.ono

    def vn_pb_json(self, filename="vn2pb.json"):
        if not self.vn_pb_jsono:
            vn_pb_jsono = json.load(open(filename))
            self.vn_pb_jsono = {normalize_vnc(k): vn_pb_jsono[k] for k in vn_pb_jsono}
        return self.vn_pb_jsono

    def vn_fn(self, filename="C:/Users/Kevin/PycharmProjects/lexical_resources/semlink/vn-fn2.s"):
        if not self.vn_fno:
            self.vn_fno = vnfn.load_mappings(filename)
        return self.vn_fno

    def vn_fn_roles(self, filename="C:/Users/Kevin/PycharmProjects/lexical_resources/semlink/1.2.2c/vn-fn/VN-FNRoleMapping.txt"):
        if not self.vn_fn_roleso:
            self.vn_fn_roleso = vnfn.load_element_mappings(mapping_file=filename)
        return self.vn_fn_roleso

    # Run full check and update - VN member/class okay, matches PB, update to VN-PB
    def update_verbnet_from_propbank(self):
        c = 0
        for ann_key in self.annotations.keys():
            ann = self.annotations[ann_key]
            if not ann.check_vn(self.vn(), update=True) and ann.check_pb(self.pb()):
                roleset = self.pb().rolesets[ann.pb_roleset]
                if len(roleset.vnc) != 1:
                    continue

                poss_vn = [annotation.check_vn(vnc, ann.verb, self.vn(), update=True) for vnc in roleset.vnc if annotation.check_vn(vnc, ann.verb, self.vn(), update=True)]

                if len(poss_vn) == 1:
                    c += 1
                    ann.vn_class = poss_vn[0]
                    logging.info("Found a new vn class in PB : " + str(ann) + " " + str(poss_vn))
                else:
                    logging.info("Match found in PB for missing VN, but didn't have singular option : " + str(ann) + " " + str(roleset))

                    for vn_class in [vnc for vnc in self.vn_pb_json().keys() if ann.pb_roleset in self.vn_pb_json()[vnc]]:
                        checked_result = annotation.check_vn(vn_class, ann.verb, self.vn(), update=True)
                        if checked_result:
                            poss_vn.append(checked_result)

                    if len(poss_vn) == 1:
                        c += 1
                        ann.vn_class = poss_vn[0]
                        logging.info("Found a new vn class in VN-PB json : " + str(ann) + " " + str(roleset.vnc))
                    else:
                        logging.info("Match found in VN-PB json, but not unique : " + str(ann) + " " + str(poss_vn))

    # loading vn annotations from recently redone semlink annotation
    def update_verbnet_from_annotations(self, annotations_dir):
        for file in os.listdir(annotations_dir):
            for line in open(annotations_dir + file).readlines():
                self.add_vn(line)

    # check and update framenet mappings based on vn-fn file
    def update_framenet_from_mappings(self):
        for ann_key in self.annotations.keys():
            ann = self.annotations[ann_key]
            if not ann.check_fn(self.fn()) and ann.check_vn(self.vn()):
                k = ann.vn_class + "-" + ann.verb
                if k in self.vn_fn():
                    if len(self.vn_fn()[k]) == 1:
                        logging.info("Updated fn mapping based on vn-fn : " + str(ann) + " " + str(self.vn_fn()[k]))
                        ann.fn_frame = self.vn_fn()[k][0]
                    elif len(self.vn_fn()[k]) == 0:
                        ann.fn_frame = "NF"
                        logging.info("Results from vn-fn = NF, no mapping : " + str(ann) + " " + str(self.vn_fn()[k]))
                    else:
                        ann.fn_frame = "IN"
                        logging.info("Results from vn-fn = IN, multiple mappings : " + str(ann) + " " + str(self.vn_fn()[k]))

    # Adds and updates instances based on a PB release, preferable the new unified WSJ
    def update_propbank_from_release(self, pb_release_location):
        for folder in os.listdir(pb_release_location):
            for f in os.listdir(pb_release_location + folder):
                if f.endswith(".prop"):
                    for line in open(pb_release_location + folder + "/" + f).readlines():
                        self.add_pb(line)

    # Updates ON sense annotations from a release, likely the ON-4.99
    def update_ontonotes_from_release(self, on_release_location):
        for folder in os.listdir(on_release_location):
            for f in os.listdir(on_release_location + folder):
                if f.endswith("sense"):
                    for line in open(on_release_location + folder + "/" + f):
                        self.add_on(line)


    def update_dependencies(self):
        for ann_key in self.annotations:
            ann = self.annotations[ann_key]
            new_deps = []
            final_deps = []
            if not ann.dependencies:
                continue
            for dep in ann.dependencies:
                dep = dep.split("=")[0]
                if ann.pb_roleset in self.pb().rolesets:
                    for role_mapping_key in self.pb().rolesets[ann.pb_roleset].role_mappings:
                        if role_mapping_key in dep:
                            role_mapping = self.pb().rolesets[ann.pb_roleset].role_mappings[role_mapping_key]
                            role_mapping = {annotation.check_vn(vnc, ann.verb, self.vn(), update=True):role_mapping[vnc] for vnc in role_mapping}
                            if False in role_mapping:
                                del role_mapping[False]

                            if ann.vn_class in role_mapping:
                                dep += ";" + role_mapping[ann.vn_class].capitalize()
                new_deps.append(dep)

            for dep in new_deps:
                if ann.vn_class and ann.fn_frame and ann.vn_class + ";" + ann.fn_frame in self.vn_fn_roles():
                    role_mapping = self.vn_fn_roles()[ann.vn_class + ";" + ann.fn_frame]
                    if dep.split(";")[-1] in role_mapping:
                        dep += ";" + role_mapping[dep.split(";")[-1]]
                final_deps.append(dep)
        return

    # Add or update a SemLink instance based on a VerbNet annotation
    def add_vn(self, instance):
        vn_ann = annotation.VnAnnotation(instance)
        if vn_ann.check_vn(self.vn()):
            if vn_ann.instance not in self.annotations:
                new_ann = annotation.SemLinkAnnotation()
                new_ann.from_vn_ann(vn_ann)
                self.annotations[new_ann.instance] = new_ann
            elif not self.annotations[vn_ann.instance].vn_class:
                logging.info("Missing vn annotation, adding : " + str(vn_ann.instance) + " " + vn_ann.vn_class)
                self.annotations[vn_ann.instance].vn_class = vn_ann.vn_class
            elif self.annotations[vn_ann.instance].vn_class != vn_ann.vn_class:
                logging.info("Instance already has vn class and they don't match, updating to new annotation : " + str(self.annotations[vn_ann.instance].vn_class) + " != " + str(vn_ann.vn_class))
                self.annotations[vn_ann.instance].vn_class = vn_ann.vn_class
        elif vn_ann.vn_class:       # has a class but isn't a good class
            logging.info("New vn class is bad : '" + str(vn_ann.vn_class) + "' " + str(vn_ann.verb))
        else:
            pass
            # No annotation, don't add it. Not logging


    # Add or update a SemLink instance based on PropBank annotation
    def add_pb(self, instance):
        a = annotation.PbAnnotation(instance)
        if a.instance not in self.annotations:
            new_ann = annotation.SemLinkAnnotation()
            new_ann.from_pb_ann(a)
            self.annotations[new_ann.instance] = new_ann
        elif not self.annotations[a.instance].pb_roleset:
            logging.info("Missing pb roleset, adding : " + str(a.instance) + " " + a.pb_roleset)
            self.annotations[a.instance].pb_roleset = a.pb_roleset
        elif self.annotations[a.instance].pb_roleset != a.pb_roleset:
            logging.info("Pb roleset mismatch, rewriting with new pb annotation : " + str(self.annotations[a.instance].pb_roleset) + " replaced with " + str(a.pb_roleset))
            self.annotations[a.instance].pb_roleset = a.pb_roleset
        return


    # Updating from ON sense groupings from 4.99
    def add_on(self, instance):
        a = annotation.OnAnnotation(instance)
        if "-n" in a.verb:
            return

        if a.instance not in self.annotations:
            # shouldn't have to add new annotations from on, as they should be in pb. but maybe?
            logging.info("Not in anns??? : " + str(a.instance) + " : " + a.verb + " " + a.on_group)
        elif not self.annotations[a.instance].on_group:
            logging.info("Missing on annotation, adding : " + str(a.instance) + " " + a.on_group)
            self.annotations[a.instance].on_group = a.on_group
        elif self.annotations[a.instance].on_group != a.on_group:
            logging.info("On grouping mismatch, rewriting with new on annotation : " + str(self.annotations[a.instance].on_group) + " replaced with " + str(a.on_group))
            self.annotations[a.instance].on_group = a.on_group


    def write(self, output_file="semlink1.3"):
        with open(output_file, "w") as o:
            for a in sorted(self.annotations):
                o.write(self.annotations[a].writable() + "\n")


def counts(semlink):
    total, pb, vn, fn, on = 0, 0, 0, 0, 0
    for key in semlink.annotations:
        instance = semlink.annotations[key]
        total += 1
        if instance.pb_roleset:
            pb += 1
        if instance.vn_class:
            vn += 1
        if instance.fn_frame and instance.fn_frame != "NF" and instance.fn_frame != "IN":
            fn += 1
        if instance.on_group:
            on += 1
    print (total, pb, vn, fn, on)


def build_semlink():
    semlink = SemLink("C:/Users/Kevin/PycharmProjects/lexical_resources/semlink/1.3 instances/auto_updated_from_1.2.2c", version="1.2")
    print ("building semlink...")
    counts(semlink)

    print("updating from vn anns...")
    semlink.update_verbnet_from_annotations(VN_ANNS)
    print ("updating from pb release...")
    semlink.update_propbank_from_release(PB_RELEASE)
    counts(semlink)
    print ("updating from on release...")
    semlink.update_ontonotes_from_release(ON_RELEASE)
    print ("updating vn from pb...")
    semlink.update_verbnet_from_propbank()
    print ("updating from vn-fn mappings...")
    semlink.update_framenet_from_mappings()

    print ("updating dependency information from pb-vn-fn...")
    semlink.update_dependencies()

    semlink.write()

if __name__ == "__main__":
    build_semlink()