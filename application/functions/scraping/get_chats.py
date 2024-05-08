from application.core.scheduler import SchedulerTasker
import boto3
import json

from faker import Faker
import random
from application.models.chats_model import Chats
from application.models.reservations_model import Reservations
from application.models.properties_model import Properties
from pynamodb.exceptions import DoesNotExist
from datetime import datetime
from application.services.gpt_service import get_gpt_response

fake = Faker('es_ES')

# Lista de frases descriptivas del partner
frases_partner = [
    "La propiedad está en excelente estado.",
    "La casa cuenta con una cocina moderna y bien equipada.",
    "La propiedad incluye una plaza de aparcamiento privado.",
    "El interior de la casa ha sido recientemente renovado.",
    "La propiedad está ubicada en un barrio tranquilo.",
]

# Lista de preguntas del guest
preguntas_guest = [
    "¿Cuántos baños tiene la propiedad?",
    "¿La propiedad tiene un jardín?",
    "¿La cocina está equipada?",
    "¿La propiedad está cerca de tiendas y restaurantes?",
    "¿La propiedad tiene plaza de aparcamiento?",
    "¿Cuantas habitaciones hay?",
    "¿Que puntuaciones ha tenido la propiedad anteriormente?",
    "¿Donde está ubicada la propiedad?",
    "¿Cual es el precio final de la reserva?",
    "¿Cuantas personas pueden alojarse en la propiedad?",
    "¿Quien ha hecho la reserva?",

]


@SchedulerTasker.task('get_chats')
def get_chats(event, context): # Función que mirará si hay nuevos mensajes de clientes
    print("Revisando si hay nuevos mensajes de clientes")

    # Generar datos de conversación simulados
    conversacion_id = fake.uuid4()
    mensajes = []

    # Escanea todas las reservas y las pone en una lista
    reservas = list(Reservations.scan())
    # Verifica si la lista está vacía
    if not reservas:
        print("No existen reservas para asignar a la conversación.")
    # Selecciona una reserva al azar
    reserva = random.choice(reservas)
    client_name = reserva.client_name
    # Usa la pk de la reserva para crear la pk de la conversación
    user_name, propiedad_id, reserva_id = reserva.pk.split("#")
    reserva_dict = reserva.to_dict()

    propiedades = list(Properties.scan())
    if not propiedades:
        print("No existen propiedades para asignar a la conversación.")
    # Selecciona una propiedad al azar
    propiedad = random.choice(propiedades)
    propiedad_dict = propiedad.to_dict()

    num_mensajes = random.randint(1, 4)  # Selecciona de 1 a 3 mensajes

    # Asegurarse de que no se soliciten más mensajes de los disponibles
    num_mensajes = min(num_mensajes, len(frases_partner))

    frases_partner_unicas = random.sample(frases_partner, num_mensajes)

    for content in frases_partner_unicas:
        author = "partner"
        mensajes.append({"author": author, "content": content})

    # El último mensaje es una pregunta del guest
    mensajes.append({"author": "guest", "content": random.choice(preguntas_guest)})

    context = {
        "mensajes": mensajes,
        "property": propiedad_dict,
        "reservation": reserva_dict
    }

    print(mensajes)

    respuesta= get_gpt_response(context)
    print("Chat GPT ha respondido\n" +respuesta)

    mensajes.append({"author": "partner", "content": respuesta})

    conversacion = Chats(
        pk=f"{user_name}#{propiedad_id}#{reserva_id}#{conversacion_id}",
        sk=datetime.now().isoformat(),
        sender=user_name,
        receiver=client_name,
        response=mensajes
    )


    conversacion_dict = conversacion.to_dict()

    conversacion.save()

    print("Conversación guardada:", conversacion_dict)




