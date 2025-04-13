from ..models import Folder, Resource

def save_bpmn_to_db(process_def, folder: Folder):
    """
    Save BPMN process definition to database
    """
    for element in process_def.elements:
        Resource.objects.create(
            folder=folder,
            name=element.name or element.id,
            description=f"Type: {element.__class__.__name__}"
        )
