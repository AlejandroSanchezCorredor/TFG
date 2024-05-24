from pynamodb.attributes import UnicodeAttribute, MapAttribute, ListAttribute
from application.core.pynamodb import BaseModel
import json

class Chats(BaseModel):
    class Meta:
        table_name = 'Chats'
        region = 'eu-west-3'
    
    pk = UnicodeAttribute(hash_key=True)
    sk = UnicodeAttribute(range_key=True) # La sk será la fecha de la conversacion/respuesta ChatGpt
    sender  = UnicodeAttribute()
    receiver = UnicodeAttribute()
    response = ListAttribute(of=MapAttribute) # Es una lista de diccionarios (o de Mapas, como se llaman en DynamoDB)

    def to_dict(self):
        return {
            'pk': self.pk,
            'sk': self.sk,
            'emisor': self.sender,
            'receptor': self.receiver,
            'response': [message for message in self.response], 
        }
    