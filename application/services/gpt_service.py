import os
from openai import OpenAI
import json
from application.core.aws.ses import send_email
from application.services.twilio_service import send_to_whatsapp


def get_gpt_response(message): 
    context = json.dumps(message)
    key = os.getenv('CHATGPT_API_KEY', None)
    # Con los datos simulados detecta que las preguntas del cliente no tienen respuesta y responde a todas
    prompt = [{
        'role': 'system',
        'content': f"""Eres un asistente cuyo deber es responder preguntas automáticamente de manera breve y precisa que tengan que ver un propiedades y reservas. \
        Tu tarea es responder preguntas que realicen los clientes sobre propiedades y reservas de las que tengas contexto de manera breve. \
        Sigue estos pasos: \
        Paso 1: Identifica la conversación en el JSON, está en la clave "mensajes". \
        Paso 2: Identifica al cliente, que tendrá dentro de "mensajes", dentro de "response" y dentro de "author", el campo "guest". \
        Paso 3: Verifica si las preguntas del cliente tienen respuesta. \
        Paso 4: Si no existen preguntas sin responder, respode "No hay preguntas sin responder". \
        Paso 5: Responde únicamente a las preguntas que no tengan respuesta. \
        Paso 6: Verifica si la pregunta está relacionada con la propiedad o la reservas. \
        Paso 7: Verifica si tienes la respuesta a dicha pregunta dentro del contexto . \
        Paso 8: Si los pasos 5 y 6 se cumple, responde a la pregunta. En caso contrario, responde "No definido". \
        Paso 9: Si tienes más de una pregunta sin responder, solo muestra las respuestas separadas por un punto y coma y repite los pasos anteriores. \
        La respuesta debe ser breve y en lenguaje humano. \
        Tómate tu tiempo para responder como lo haría el propietario de la propiedad. \
        Responde de manera humanizada y únicamente a las que estén relacionadas con las propiedades y reservas. \
        No mientas y responde solo a las preguntas de las que tengas contexto. \
        Aquí está todo el contexto de la situación: \
        {context}"""
            }]

    client = OpenAI(api_key=key)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=prompt,
        temperature=0,
    )

    content = response.choices[0].message.content

    # Formatear la respuesta para que se parezca lo máximo posible a una respuesta humana

    index = content.find("sin responder")
    # Si la frase fue encontrada, cogemos todo después del segundo ":", que será el contenido que nos interesa
    if index != -1:
        # Encuentra el segundo ":" después de "sin responder"
        second_colon = content.find(":", index + len("sin responder"))

        # Si se encontró un segundo ":", coge todo después de eso
        if second_colon != -1:
            content = content[second_colon+1:].strip()
        else:
            content = content
    else:
        content = content

    #number = '+34601364570' # Obtendríamos el número del cliente de la tabla donde almacenamos las reservas
    #send_to_whatsapp(content,number)

    #if "no definido" in content or "no especific" in content or "no se especifi" in content: # COGER MÁS IF DEL METODO GET_GTP_RESPONSE_1
        #content = 'No definido'
        #msg = "Pregunta sin contexto recibida"
        #send_email(msg, recipient="alech.maria@hotmail.com", subject="Resultado de la prueba")

    return content




   

   
