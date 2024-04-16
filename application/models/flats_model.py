from pynamodb.attributes import UnicodeAttribute
from application.core.pynamodb import BaseModel
from pynamodb.attributes import UnicodeAttribute

class Flats(BaseModel):
    class Meta:
        table_name = 'Flats'
        region = 'eu-west-3'
    
    pk = UnicodeAttribute(hash_key=True)
    flat_name = UnicodeAttribute()
    user_name = UnicodeAttribute()
    description = UnicodeAttribute()
    score = UnicodeAttribute()
    price = UnicodeAttribute()
    location = UnicodeAttribute()

    def to_dict(self):
            return {
                'pk': self.pk,
                'flat_name': self.flat_name,
                'user_name': self.user_name,
                'description': self.description,
                'score': self.score,
                'price': self.price,
                'location': self.location,
            }