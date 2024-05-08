from pynamodb.attributes import UnicodeAttribute
from application.core.pynamodb import BaseModel
from pynamodb.attributes import UnicodeAttribute, UTCDateTimeAttribute


class Reservations(BaseModel):
    class Meta:
        table_name = 'Reservations'
        region = 'eu-west-3'
    
    pk = UnicodeAttribute(hash_key=True)
    sk = UnicodeAttribute(range_key=True) # La sk será la fecha de entrada (check_in_date)
    check_out_date = UnicodeAttribute()
    bedrooms_n = UnicodeAttribute()
    people_n = UnicodeAttribute()
    price = UnicodeAttribute()
    idiom = UnicodeAttribute()
    client_name = UnicodeAttribute() # Nombre de la persona que ha hecho la resrva


    def to_dict(self):
            return {
                'pk': self.pk,
                'sk': self.sk,
                'check_out_date': self.check_out_date,
                'bedrooms_n': self.bedrooms_n,
                'people_n': self.people_n,
                'price': self.price,
                'idiom': self.idiom,
                'client_name': self.client_name,
            }


    
