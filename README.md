# semlink
Official repository for the Semlink 2 resource

SemLink consists of two main components: mapping files between resources (PropBank, VerbNet, and FrameNet), as well as annotated instances. These instances are predicates in the Ontonotes corpora; they contain annotation for the above three resources as well as OntoNotes sense groups and argument annotations. Not all instances contain annotation for all resources: we aimed at improving the size and consistency of SemLink in the latest release, so more instances were added that don't contain every resource, and a small number of annotations were removed due to inconsistencies with the new versions of the resources.

The new new version of SemLink is designed to handle the latest versions of each of its linked resources: VerbNet 3.3, the Unified PropBank frame files, and FrameNet 1.7. This involved manual and automatic updates to mappings and annotations. We also expanded the SemLink instances by bringing in additional PropBank and VerbNet-annotated instances and automatically populating their mappings.

This codebase consists of a number of resources:

    -semlink2
        -semlink2.instances
        -pb-vn2.json
        -vn-fn2.json
    -lexical_resources
        -propbank-frames-master
        -verbnet-master
    -other_resources
        -a number of supporting files
    -tools
        -scripts for handling data/creating semlink
        
The <code>semlink2</code> folder contains the final annotated instances (<code>semlink2.instances</code>) as well as mapping files between PropBank and VerbNet (<code>pb-vn2.json</code>) and between VerbNet and FrameNet (<code>pb-fn2.json</code>)

The remaining directories are used to build and validate the SemLink 2 version from their respective resources.

# Examples
Loading mapping files

```python
import json

pb_vn_mappings = json.load(open("instances/pb-vn2.json"))
vn_fn_mappings = json.load(open("instances/vn-fn2.json"))
```

## Using PB-VN mappings
To find which VerbNet senses a roleset in PB maps to:

```python
verb, roleset = "shake", "01"

vn_mappings = pb_vn_mappings[sense + "." + verb]
```

This yields a dictionary keyed by verb sense for all the VN classes that map to that particular roleset.

```python
for vn_class_number in vn_mappings:
    arg_mappings = vn_mappings[vn_class_number]
```

## Using VN-FN mappings
To find which FrameNet frames a particular verb sense in VN belongs to:
```python
verb, vn_class = "shake", "26.5"
framenet_mappings = vn_fn_mappings[vn_class + "-" + verb]
```

## PB to FN
We don't include direct links from PB to FN, but they can be retrieved through VN.

```python
    # Let's get the FN mappings from the PB roleset "abduct.01"
    vn_mapping = pb_vn_mappings["abduct.01"]    

    # Here we just grab the first sense
    vn_class = list(vn_mapping.keys())[0]

    # From VN, abduct.01 maps to VerbNet class 10.5
    fn_mapping = vn_fn_mappings[vn_class + "-" + verb]

    print (fn_mapping)
    # And from FN we get the Frame "kidnapping"
```


## Role to Role Mappings
Moving from PB to VN roles can be done through the pb-vn2.json
```python 
for vn_mapping in vn_mappings:
    vn_class, arg_mappings = vn_mapping["vnclass"], vn_mappings["args"]
    print (arg_mappings)
```
These are lists of tuples containing the PB arg (ARG0, ARG1), etc, and their mappings to the respective VN thematic roles (Agent, Patient)

Moving to FrameNet frame arguments requires again moving through VerbNet. We are currently (22.03.2021) in the process of providing updated mappings from VN roles to FN arguments.


## Loading annotated instances
This can be done using annotation.py tool

```python
import annotation
instances = []
        
for line in open(instances/semlink-2).readlines():
    instances.append(annotation.SemLinkAnnotation(line))
```

## Generating a new SemLink
This can be done using the SemLink.py script. It needs to be provided a number of resources: VerbNet, PropBank, and Ontonotes Sense Groupings (FrameNet is handled via the NLTK api). These (and other additions) can be configured using config.py. Once configured, calling the script will attempt to build a set of instances validated against the provided resources.

```
python SemLink.py
```

## Other use cases
Please feel free to leave an issue on the Github if you have other use cases you'd like to see. 

## Citing
If you use SemLink in your work, please cite our IWCS paper:
```
@inproceedings{stowe-2021,
    title = "SemLink 2.0: Chasing Lexical Resources",
    author = "Stowe, Kevin and Preciado, Jenette and Conger, Kathryn, and Brown, Susan Windisch and Kazeminejad, Ghazaleh and Palmer, Martha",
    booktitle = "30th Annual Meeting of the Association for Computational Linguistics",
    year = "2021",
    address = "Gronigen, Netherlands",
    publisher = "Association for Computational Linguistics",
    url = "https://iwcs2021.github.io/proceedings/iwcs/pdf/2021.iwcs-1.21.pdf",
    pages = "222--227",
}
```
