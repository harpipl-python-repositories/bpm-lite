from dataclasses import dataclass
from .base import BpmnElement
from .decorators import register_bpmn_tag


@register_bpmn_tag("userTask")
@dataclass
class UserTaskDef(BpmnElement):
    id: str
    name: str

    @classmethod
    def from_xml(cls, elem):
        return cls(id=elem.attrib["id"], name=elem.attrib.get("name", ""))


@register_bpmn_tag("exclusiveGateway")
@dataclass
class GatewayDef(BpmnElement):
    id: str
    name: str
    gateway_type: str

    @classmethod
    def from_xml(cls, elem):
        return cls(
            id=elem.attrib["id"],
            name=elem.attrib.get("name", ""),
            gateway_type="exclusive",
        )


@register_bpmn_tag("serviceTask")
@dataclass
class ServiceTaskDef(BpmnElement):
    id: str
    name: str
    implementation: str = ""

    @classmethod
    def from_xml(cls, elem):
        return cls(
            id=elem.attrib["id"],
            name=elem.attrib.get("name", ""),
            implementation=elem.attrib.get("implementation", ""),
        )


@register_bpmn_tag("startEvent")
@dataclass
class StartEventDef(BpmnElement):
    id: str
    name: str

    @classmethod
    def from_xml(cls, elem):
        return cls(id=elem.attrib["id"], name=elem.attrib.get("name", ""))
