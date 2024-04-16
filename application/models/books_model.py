from pynamodb.attributes import UnicodeAttribute
from application.core.pynamodb import BaseModel
from pynamodb.attributes import UnicodeAttribute, UTCDateTimeAttribute


class Books(BaseModel):
    class Meta:
        table_name = 'Books'
        region = 'eu-west-3'
    
    pk = UnicodeAttribute(hash_key=True)
    sk = UnicodeAttribute(range_key=True) # La sk será la fecha de entrada (check_in_date)
    check_out_date = UnicodeAttribute()
    bedrooms_n = UnicodeAttribute()
    childens_n = UnicodeAttribute()
    adults_n = UnicodeAttribute()

    def to_dict(self):
            return {
                'pk': self.pk,
                'sk': self.sk,
                'check_out_date': self.check_out_date,
                'bedrooms_n': self.bedrooms_n,
                'childens_n': self.childens_n,
                'adults_n': self.adults_n,
            }


    
