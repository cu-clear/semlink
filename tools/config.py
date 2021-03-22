"""Semlink Config

Generating semlink requires a number of resources. We provide the frames for the unified PB files, the 3.4 version of
VerbNet, and the OntoNotes sense groupings in the "lexical_resources" folder.

Additional annotation files can also be added to expand the number of instances. PB instances can be retrieved from their
GitHub, however, VN and ON annotations used in the original are not available due to licensing issues.

A number of linking files are also used; these are included in "other_resources", along with additional resources
including VN common objects and the old (1.2.2c) version of instances.
"""
resource_root = "../lexical_resources/"
other_root = "../other_resources/"

#Lexical resources: PB, VN, ON
PB_RESOURCE_PATH = resource_root + "propbank-frames-master/frames/"
VN_RESOURCE_PATH = resource_root + "verbnet-master/verbnet-master/verbnet3.4/"
ON_RESOURCE_PATH = resource_root + ""

# Annotations
# PropBank annotations used can be retrieved from their GitHub:
# https://github.com/propbank/propbank-release/
PB_ANNS_PATH = other_root + "propbank-release-master/data/ontonotes/nw/wsj/"

# VN and ON Anns fall under a variety of licenses - we are looking into solutions for releasing
ON_ANNS_PATH = other_root + ""
VN_ANNS_PATH = other_root + ""

# Extra files
OLD_VERSION_PATH = other_root + "1.2.2c.okay"                  # old version of instances
EXTERNAL_VN2PB_PATH = other_root + "external_vn2pb.json"       # manual curated mappings from vn2pb, done at CU
OLD_VN2FN_PATH = other_root + "vn-fn.s"                        # old mappings, used for some updates
VN2FN_PATH = other_root + "vn-fn2.s"                           # another version of mappings, in XML instead of json
VN2FN_ROLES_PATH = other_root + "VN-FNRoleMapping.txt"         # Role mappings. Please note the roles file is extremely out of date. Updating is underway
