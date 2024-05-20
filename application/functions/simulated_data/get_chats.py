import random
from faker import Faker
from application.core.scheduler import SchedulerTasker
from application.core.aws.ses import send_email
from application.models.properties_model import Properties
from application.models.reservations_model import Reservations
from application.functions.faker.create_fake_chat import create_fake_conversation
from application.core.configuration_loader import get_configuration

fake = Faker('es_ES')

@SchedulerTasker.task('get_chats')
def get_chats(event, context):
    configuration = get_configuration()
    
    print("Revisando si hay nuevos mensajes de clientes")

    if random.random() < 0.6:
        try:
            properties = list(Properties.scan())
        except Exception as e:
            msg = "No existen propiedades para asignar a la conversacion."
            send_email(msg, recipient="alech.maria@hotmail.com", subject="Obtención de mensajes sin responder")
            return None
        
        property = random.choice(properties) # Obtengo la propiedad a la que va a estar relacionada la conversación
        dict_property = property.to_dict()
        print("Propiedad obtenida: " + str(dict_property))
        user_name, propiedad_id = property.pk.split("#")

        try:
            reservations = list(Reservations.scan())
        except Exception as e:
            msg = "No existen reservas para asignar a la conversacion."
            send_email(msg, recipient=configuration.SES_EMAIL_SENDER, subject="Obtención de mensajes sin responder")
            print(msg)
            return None

        # Obtengo solo la reserva a la que pertenezca la propiedad obtenida
        filtered_reservations = [res for res in reservations if res.pk.startswith(f"{user_name}#{propiedad_id}")]

        if not filtered_reservations:
            msg = "No existen reservas para la propiedad seleccionada."
            send_email(msg, recipient=configuration.SES_EMAIL_SENDER, subject="Obtención de mensajes sin responder")
            print(msg)
            return None

        reservation = random.choice(filtered_reservations) # Obtengo la reserva a la que va a estar relacionada la conversación
        client_name = reservation.client_name
        _, _, reserva_id = reservation.pk.split("#")
        dict_reservation = reservation.to_dict()
        print("Reserva obtenida: " + str(dict_reservation))

        print("Creando una nueva conversación")
        conversation= create_fake_conversation(fake, client_name, user_name, propiedad_id, reserva_id, dict_property, dict_reservation, configuration)
        print("Conversación creada: " + str(conversation))
        msg = "Se ha creado una nueva conversación : " + str(conversation)
        print(msg)
        send_email(msg, recipient=configuration.SES_EMAIL_SENDER, subject="Obtención de conversaciones/mensajes sin responder")

    else:
        msg = "No hay mensajes sin responder de clientes"
        send_email(msg, recipient=configuration.SES_EMAIL_SENDER, subject="Obtención de mensajes sin responder")
        print(msg)






