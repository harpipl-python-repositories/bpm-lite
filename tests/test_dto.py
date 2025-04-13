import xml.etree.ElementTree as ET
from xml.etree.ElementTree import fromstring
from repository.bpmn.dto import UserTaskDef, GatewayDef, ServiceTaskDef, StartEventDef

def test_user_task_from_xml():
    # given
    xml = '<userTask id="task1" name="Approve request" />'
    elem = ET.fromstring(xml)

    # when
    task = UserTaskDef.from_xml(elem)

    # then  
    assert task.id == "task1"
    assert task.name == "Approve request"

def test_gateway_from_xml():
    # given
    xml = '<exclusiveGateway id="gateway1" name="Approve request" />'
    elem = ET.fromstring(xml)

    # when
    gateway = GatewayDef.from_xml(elem)

    # then
    assert gateway.id == "gateway1"
    assert gateway.name == "Approve request"

def test_service_task_from_xml():
    xml = '<serviceTask id="task2" name="Send Email" implementation="mailService" />'
    elem = fromstring(xml)

    task = ServiceTaskDef.from_xml(elem)

    assert task.id == "task2"
    assert task.name == "Send Email"
    assert task.implementation == "mailService"

def test_start_event_from_xml():
    xml = '<startEvent id="start1" name="Start" />'
    elem = fromstring(xml)

    start = StartEventDef.from_xml(elem)

    assert start.id == "start1"
    assert start.name == "Start"