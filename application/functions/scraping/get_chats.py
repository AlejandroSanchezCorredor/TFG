from application.core.scheduler import SchedulerTasker
import boto3
import json

@SchedulerTasker.task('get_chats')
def get_chats(event, context): # Función que mirará si hay nuevos mensajes de clientes
    print("Revisando si hay nuevos mensajes de clientes")



