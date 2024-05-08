from pynamodb.attributes import UnicodeAttribute
from application.core.pynamodb import BaseModel
from pynamodb.attributes import UnicodeAttribute

class Properties(BaseModel):
    class Meta:
        table_name = 'Properties'
        region = 'eu-west-3'
    
    pk = UnicodeAttribute(hash_key=True)
    property_name = UnicodeAttribute()
    description = UnicodeAttribute()
    scores = UnicodeAttribute() # No es un diccionario porque lo transformamos antes a una cadena JSON
    location = UnicodeAttribute()

    def to_dict(self):
            return {
                'pk': self.pk,
                'property_name': self.property_name,
                'description': self.description,
                'scores': self.scores,
                'location': self.location,
            }