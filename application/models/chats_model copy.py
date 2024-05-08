'''
from pynamodb.attributes import UnicodeAttribute, MapAttribute, ListAttribute
from application.core.pynamodb import BaseModel
import json

class MessageAttribute(MapAttribute): # Segundo diccionario
    author = UnicodeAttribute()
    content = UnicodeAttribute()

    def to_dict(self):
        return {
            'author': self.author,
            'content': self.content,
        }

class OuterMap(MapAttribute): # Primer diccionario
    M = MessageAttribute()

    def to_dict(self):
        return {
            'M': self.M.to_dict() if self.M else None,
        }

class Chats(BaseModel):
    class Meta:
        table_name = 'Chats'
        region = 'eu-west-3'
    
    pk = UnicodeAttribute(hash_key=True)
    sk = UnicodeAttribute(range_key=True) # La sk será la fecha de la conversacion/respuesta ChatGpt
    sender  = UnicodeAttribute()
    receiver = UnicodeAttribute()
    response = ListAttribute(of=OuterMap) # Es una lista de diccionarios

    def to_dict(self):
        return {
            'pk': self.pk,
            'sk': self.sk,
            'sender': self.sender,
            'receiver': self.receiver,
            'response': [message.M.to_dict() for message in self.response],
        }
'''