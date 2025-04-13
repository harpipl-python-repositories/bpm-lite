class BpmnElement:
    _bpmn_tag = None
    
    @classmethod
    def from_xml(cls, elem):
        raise NotImplementedError("Subclasses must implement this method")