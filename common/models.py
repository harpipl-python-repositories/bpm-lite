from django.db import models
import uuid

class AbstractModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.__class__.__name__} {self.id}"


class AbstractRootModel(AbstractModel):
    logical_id = models.CharField(default=uuid.uuid4, editable=False, max_length=40, unique=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.__class__.__name__} {self.logical_id}"