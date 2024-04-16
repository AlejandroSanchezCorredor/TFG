from pynamodb.attributes import UnicodeAttribute
from application.core.pynamodb import BaseModel
from pynamodb.attributes import UnicodeAttribute, UTCDateTimeAttribute


class Chats(BaseModel):
    class Meta:
        table_name = 'Chats'
        region = 'eu-west-3'
    
    pk = UnicodeAttribute(hash_key=True)
    sk = UnicodeAttribute(range_key=True) # La sk será la fecha de la conversacion/respuesta ChatGpt
    sender  = UnicodeAttribute()
    receiver = UnicodeAttribute()
    response = UnicodeAttribute()

    def to_dict(self):
            return {
                'pk': self.pk,
                'sk': self.sk,
                'sender': self.sender,
                'receiver': self.receiver,
                'response': self.response,
            }
 