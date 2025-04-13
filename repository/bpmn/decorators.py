def register_bpmn_tag(tag_name):
    def decorator(cls):
        cls._bpmn_tag = tag_name
        return cls

    return decorator
