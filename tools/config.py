# Put the required resources in the "data" folder, or change the pointer

resource_root = "../lexical_resources/"
other_root = "../other_resources/"

PB_RESOURCE_PATH = resource_root + "propbank-frames-master/frames/"

# PropBank annotations used can be retreived from their GitHub:
# https://github.com/propbank/propbank-release/
PB_ANNS_PATH = other_root + "propbank-release-master/data/ontonotes/nw/wsj/"

ON_RESOURCE_PATH = resource_root + ""

# VN Anns fall under license - we are looking into solutions for releasing
ON_ANNS_PATH = other_root + ""

VN_RESOURCE_PATH = resource_root + "verbnet-master/"

# VN Anns fall under a variety of licenses - we are looking into solutions for releasing
VN_ANNS_PATH = other_root + ""

OLD_VERSION_PATH = other_root + "1.2.2c.okay"
EXTERNAL_VN2PB_PATH = other_root + "external_vn2pb.json"
VN2FN_PATH = other_root + "vn-fn2.s"

# Please note the roles file is extremely out of date. Updating is underway
VN2FN_ROLES_PATH = other_root + "VN-FNRoleMapping.txt"