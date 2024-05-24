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
                'check_in_date': self.sk,
                'check_out_date': self.check_out_date,
                'num_habitaciones': self.bedrooms_n,
                'num_personas': self.people_n,
                'precio': self.price,
                'idioma_preferencia': self.idiom,
                'nombre_cliente': self.client_name,
            }


    
