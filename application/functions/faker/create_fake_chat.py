import random
from datetime import datetime
import os
from application.models.chats_model import Chats
from application.core.aws.ses import send_email
from application.services.gpt_service import get_gpt_response
from application.core.configuration_loader import get_configuration

MIN_N_MESSAGES = 2
MAX_N_MESSAGES = 4

def load_texts_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file.readlines()]

# Obtenemos la ruta absoluta del directorio actual
current_dir = os.path.dirname(os.path.abspath(__file__))

# Texto simulado que el propietario podría enviar a su cliente
partner_text = load_texts_from_file(os.path.join(current_dir, 'utils', 'partner_text.txt'))

# Lista de preguntas del guest que podría realizar el cliente al propietario
guest_questions = load_texts_from_file(os.path.join(current_dir, 'utils', 'guest_questions.txt'))

def create_fake_conversation(fake, client_name, user_name, propiedad_id, reserva_id, dict_property, dict_reservation, configuration):
    id_conversation = fake.uuid4()
    conversation_pk = f"{user_name}#{propiedad_id}#{reserva_id}#{id_conversation}"
    messages = []
    total_n_messages = random.randint(MIN_N_MESSAGES, MAX_N_MESSAGES)  # Selecciona de 2 a 4 mensajes para la conversación
    n_messages = min(total_n_messages, len(partner_text), len(guest_questions))  # No se deben solicitar más mensajes de los disponibles
    unique_partner_text = random.sample(partner_text, n_messages) # Selecciona mensajes únicos para simular conversaciones "reales"
    unique_guest_questions = random.sample(guest_questions, n_messages)

    for i in range(n_messages):
        messages.append({"author": "partner", "content": unique_partner_text[i]})
        messages.append({"author": "guest", "content": unique_guest_questions[i]})

    # El último mensaje es una pregunta que hace el cliente (guest)
    remaining_questions = [q for q in guest_questions if q not in unique_guest_questions] # Selecciona las preguntas restantes que el "guest" no ha hecho aún
    messages.append({"author": "guest", "content": random.choice(remaining_questions)})

    context = {
        "mensajes": messages,
        "property": dict_property,
        "reservation": dict_reservation
    }

    gpt_answer= get_gpt_response(context)
    msg = "Chat GPT ha respondido\n" + gpt_answer + " a la conversación : " + conversation_pk
    send_email(msg, recipient=configuration.SES_EMAIL_SENDER, subject="Guardando conversación")

    messages.append({"author": "partner", "content": gpt_answer})

    conversacion = Chats(
        pk=conversation_pk,
        sk=datetime.now().isoformat(),
        sender=user_name,
        receiver=client_name,
        response=messages
    )
    conversacion_dict = conversacion.to_dict()

    try:
        conversacion.save()
    except Exception as e:
        msg = "Error al guardar la conversación en la base de datos."
        send_email(msg, recipient=configuration.SES_EMAIL_SENDER, subject="Guardando conversación")
    
    return conversacion_dict
