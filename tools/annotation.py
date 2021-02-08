def check_vn(vn_class, verb, vn, update=False):
    if not vn_class:
        return False
    if vn_class in vn.verb_classes_numerical_dict:
        if verb in [m.name for m in vn.verb_classes_numerical_dict[vn_class].members]:
            return vn_class
    if update:
        if vn_class not in vn.verb_classes_numerical_dict:
            if vn_class.split("-")[0] in vn.verb_classes_numerical_dict:
                vn_class = vn_class.split("-")[0]
            else:
                return False

        for subclass in [vn.verb_classes_numerical_dict[vn_class.split("-")[0]]] + vn.verb_classes_numerical_dict[vn_class.split("-")[0]].get_all_subclasses():
            if verb in [m.name for m in subclass.get_members()]:
                return subclass.numerical_ID
    return False

class Annotation(object):
    def __init__(self):
        self.dep = None
        self.source_file = None
        self.sentence_no = None
        self.token_no = None
        self.verb = None
        self.vn_class = None
        self.fn_frame = None
        self.pb_roleset = None
        self.on_group = None
        self.dependencies = None
        self.instance = None
        self.source = None

    def __hash__(self):
        return hash(self.__str__())

    def __eq__(self, other):
        if self.source_file == other.source_file and self.sentence_no == other.sentence_no and self.token_no == other.token_no and self.verb == other.verb:
            return True
        else:
            return False

    def __str__(self):
        return str([self.instance, self.verb, self.vn_class, self.pb_roleset, self.on_group, self.fn_frame, self.source])

    def __lt__(self, other):
        if int(self.source_file.split("/")[-1][4:8]) != int(other.source_file.split("/")[-1][4:8]):
            return int(self.source_file.split("/")[-1][4:8]) < int(other.source_file.split("/")[-1][4:8])
        if int(self.sentence_no) != int(other.sentence_no):
            return int(self.sentence_no) < int(other.sentence_no)
        if int(self.token_no) != int(other.token_no):
            return int(self.token_no) < int(other.token_no)
        return 0

    def __gt__(self, other):
        if not self.__lt__(other):
            return 1
        return

    # Verify that this instance has a vn class, and the class/member pair is valid for a certain VN version
    def check_vn(self, vn, update=False):
        return check_vn(self.vn_class, self.verb, vn, update=update)

    def check_pb(self, pb):
        if self.pb_roleset and self.pb_roleset in pb.rolesets:
            return True
        return False

    def check_on(self, on):
        if self.on_group and self.verb + "-v-" + self.on_group in on.groupings.keys():
            return True
        return False

    def check_fn(self, fn):
        if not self.fn_frame or self.fn_frame in ["IN", "NF"]:
            return False
        poss_frames = fn.frames_by_lemma(self.verb)
        if self.fn_frame and self.fn_frame in [f.name for f in poss_frames]:
            return True
        return False

    def writable(self):
        return str(self)

class VnAnnotation(Annotation):
    def __init__(self, line):
        super().__init__()
        attr_list = line.split()
        self.source_file = attr_list[0].split("/")[-1]
        self.sentence_no = attr_list[1]
        self.token_no = attr_list[2]
        self.verb = attr_list[3][:-2] if attr_list[3].endswith("-v") else attr_list[3]

        self.vn_class = attr_list[4] if attr_list[4] != "None" else None
        if self.vn_class and self.vn_class[0] not in [0-9]:
            self.vn_class = "-".join(self.vn_class.split("-")[1:])

        self.instance = self.source_file + " " + self.sentence_no + " " + self.token_no
        self.source = "vn"

    def exists_in(self, vn):
        return True if (check_vn(self.vn_class, self.verb, vn)) else False

    def writable(self):
        return self.instance + " " + self.verb + " " + str(self.vn_class)

class PbAnnotation(Annotation):
    def __init__(self, line):
        super().__init__()

        attr_list = line.split()
        self.source_file = attr_list[0].split("/")[-1]
        self.sentence_no = attr_list[1]
        self.token_no = attr_list[2]
        self.verb = attr_list[4][:-2] if attr_list[4].endswith("-v") else attr_list[4]

        self.pb_roleset = attr_list[5]
        self.dependencies = attr_list[6:]

        self.instance = self.source_file + " " + self.sentence_no + " " + self.token_no
        self.source = "pb"

class OnAnnotation(Annotation):
    def __init__(self, line):
        super().__init__()

        attr_list = line.split()
        self.source_file = attr_list[0].split("/")[-1]
        self.sentence_no = attr_list[1]
        self.token_no = attr_list[2]
        self.verb = attr_list[3][:-2] if attr_list[3].endswith("-v") else attr_list[3]

        self.on_group = attr_list[4]

        self.instance = self.source_file + " " + self.sentence_no + " " + self.token_no
        self.source = "on"

class SemLinkAnnotation(Annotation):
    def __init__(self, line=None):
        super().__init__()

        if line:
            self.from_semlink_line(line)

    def from_semlink_line(self, line):
        self.input_line = line.strip()
        attr_list = line.split()

        self.source_file = attr_list[0].split("/")[-1]
        self.sentence_no = attr_list[1]
        self.token_no = attr_list[2]
        self.instance = self.source_file + " " + self.sentence_no + " " + self.token_no

        if "-v" in attr_list[3] or attr_list[3] != "gold":
            attr_list.insert(3, "gold")

        self.verb = attr_list[4][:-2] if attr_list[4].endswith("-v") else attr_list[4]
        self.vn_class = attr_list[5]
        self.fn_frame = attr_list[6]
        self.pb_roleset = attr_list[7]
        self.on_group = attr_list[8] if attr_list[8] != "null" else None
        self.source = "old sl"

        if len(attr_list) > 8:
            self.dependencies = attr_list[9:]

    # rewrite these two as generic a generic 'populate from other object' \/
    def from_vn_ann(self, vn_ann):
        self.dep = vn_ann.dep
        self.source_file = vn_ann.source_file
        self.sentence_no = vn_ann.sentence_no
        self.token_no = vn_ann.token_no
        self.verb = vn_ann.verb
        self.vn_class = vn_ann.vn_class

        self.instance = vn_ann.instance
        self.source = vn_ann.source

    def from_pb_ann(self, pb_ann):
        self.dep = pb_ann.dep
        self.source_file = pb_ann.source_file
        self.sentence_no = pb_ann.sentence_no
        self.token_no = pb_ann.token_no
        self.verb = pb_ann.verb
        self.pb_roleset = pb_ann.pb_roleset
        self.vn_class = None
        self.instance = pb_ann.instance
        self.source = pb_ann.source
        self.dependencies = pb_ann.dependencies

    # Verify that the VN and PB mapping is good. Should have pb/vn individually verified first?
    def check_pb_vn(self, pb, vn, vn_pb_json):
        vn_pb_json = {k[k.index("-") + 1:]: vn_pb_json[k] for k in vn_pb_json}
        if (not self.pb_roleset or not self.vn_class) or not self.check_vn(
                vn) or self.pb_roleset not in pb.rolesets:
            return False

        roleset = pb.rolesets[self.pb_roleset]
        if self.vn_class in roleset.vnc:
            print("matched pb frame file : " + self.vn_class + " " + self.pb_roleset)
            return True
        elif self.vn_class in vn_pb_json and self.pb_roleset in vn_pb_json[self.vn_class]:
            print("matched json : " + self.vn_class + " " + self.pb_roleset)
            return True
        else:
            print("didn't match : " + self.vn_class + " " + self.pb_roleset)
            for entry in vn_pb_json[self.vn_class]:
                if entry.startswith(self.verb):
                    self.pb_roleset = entry
                    print("  updated roleset mapping from to " + self.pb_roleset)
                    return True
            return False

    def writable(self):
        res = self.instance + " " + self.verb
        res += " " + self.vn_class if self.vn_class else " None"
        res += " " + self.fn_frame if self.fn_frame else " None"
        res += " " + self.pb_roleset if self.pb_roleset else " None"
        res += " " + self.on_group if self.on_group else " None"
        res += " " + " ".join(self.dependencies) if self.dependencies else " None"
        return res
