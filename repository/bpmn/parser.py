import xml.etree.ElementTree as ET
from .base import BpmnElement
from .dto import *

BPMN_NS = "{http://www.omg.org/spec/BPMN/20100524/MODEL}"

from dataclasses import dataclass, field
from typing import List


@dataclass
class ProcessDef:
    id: str
    name: str
    elements: List[BpmnElement] = field(default_factory=list)


def discover_bpmn_parsers():
    registry = {}
    for subclass in BpmnElement.__subclasses__():
        tag = getattr(subclass, "_bpmn_tag", None)
        if tag:
            registry[tag] = subclass
    return registry


ELEMENT_PARSERS = discover_bpmn_parsers()

def parse_bpmn(xml_content: bytes) -> ProcessDef:
    root = ET.fromstring(xml_content)
    process = root.find(f"{BPMN_NS}process")

    proc_def = ProcessDef(id=process.attrib["id"], name=process.attrib.get("name", ""))

    for elem in process:
        tag = elem.tag.replace(BPMN_NS, "")
        if tag in ELEMENT_PARSERS:
            dto_class = ELEMENT_PARSERS[tag]
            proc_def.elements.append(dto_class.from_xml(elem))

    return proc_def
