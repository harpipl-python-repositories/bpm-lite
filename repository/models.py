from django.db import models
from common import models as common_models


class Folder(common_models.AbstractRootModel):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True)

    class Meta:
        db_table = "rep_folder"
        constraints = [
            models.UniqueConstraint(fields=["name"], name="unique_folder_name")
        ]

    def __str__(self):
        return self.name


class Resource(common_models.AbstractRootModel):
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True)

    class Meta:
        db_table = "rep_resource"
        constraints = [
            models.UniqueConstraint(
                fields=["folder", "name"], name="unique_resource_folder_name"
            )
        ]

    def __str__(self):
        return self.name
