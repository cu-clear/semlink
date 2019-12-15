# semlink
Official repository for the Semlink 2 resource

*We are in the process of uploading and updating resuorces. The instances and mapping files should be accurate, but the tools still require revamping to be easily useful externally. Our goal in releasing this resource via GitHub is to allow the community to be able to use these resources, but also to help validate and improve them over time. Feedback, questions, suggestions are always welcome!

SemLink consists of two main components: mapping files between resources (PropBank, VerbNet, and FrameNet), as well as annotated instances. These instances are predicates in the Ontonotes corpora; they contain annotation for the above three resources as well as OntoNotes sense groups and argument annotations. Not all instances contain annotation for all resources: we aimed at improving the size and consistency of SemLink in the latest release, so more instances were added that don't contain every resource, and a small number of annotations were removed due to inconsistencies with the new versions of the resources.

The new new version of SemLink is designed to handle the latest versions of each of its linked resources: VerbNet 3.3, the Unified PropBank frame files, and FrameNet 1.7. This involved manual and automatic updates to mappings and annotations. We also expanded the SemLink instances by bringing in additional PropBank and VerbNet-annotated instances and automatically populating their mappings.

More details, exact numbers, usability improvements, and more are coming soon.
