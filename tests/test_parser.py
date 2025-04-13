import os
from repository.bpmn.parser import parse_bpmn


def test_parse_sample_bpmn():
    # given
    with open(
        os.path.join(os.path.dirname(__file__), "resources", "sample.bpmn"), "rb"
    ) as f:
        content = f.read()

    # when
    process = parse_bpmn(content)

    # then
    assert process.id == "example-process"
    assert len(process.elements) >= 2
    assert any(e.__class__.__name__ == "UserTaskDef" for e in process.elements)
