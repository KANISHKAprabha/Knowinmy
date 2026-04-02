from import_export import resources
from .models import User # or whatever your model is

class PersonResource(resources.ModelResource):
    class Meta:
        model = User