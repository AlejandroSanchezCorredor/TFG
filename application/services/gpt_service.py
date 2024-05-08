import os
from openai import OpenAI
from twilio.rest import Client
import json
from application.core.aws.ses import send_email


# La información que le pasaremos sobre los pisos será: Nombre, comentarios, puntuaciones, direccion, estado, precio (en la página pone precios pagados por persona y noche
# pero no un precio exacto)

# La información que le pasaremos sobre la conversación será: emisor, recepto, fecha y contenido (Al final no.)

def send_to_whatsapp(gpt_response,number): # Enviamos por whatsapp la respuesta generada por ChatGPT
  from_whatsapp_number='whatsapp:+14155238886'
  # from_sms_number='+15677043718'

  # Aqui irian
  # Las credenciales

  client = Client("Credencial1", "Credencial2") # METERLAS EN EL SSM

  message = client.messages.create(
  from_= from_whatsapp_number,
  body=gpt_response,
  to= number # Cogeríamos el número de teléfono del usuario dentro de un campo de la tabla reservas
  )


def get_gpt_response(message): # Solo cogemos las respuestas ya que introduciremos en booking las respuestas scrapeando
  # "Message" contendría todo, tanto la información de los pisos como la de la conversacion, por ejemplo en formato ¿JSON?

  # En este método le pasaríamos toda la informacon definida anteriormente y el método se encargaría de llamar a la API de OpenAI

  # Nos devolverá la respuesta generada

  context = json.dumps(message)

  key = os.getenv('CHATGPT_API_KEY', None)

  prompt = [{
      'role': 'system',
      'content': f"""Eres un asistente cuyo deber es responder preguntas automáticamente. \
      Tu tarea es responder preguntas que realicen los clientes. \
      Sigue estos pasos: \
      Paso 1: Identifica la conversación en el JSON, está en la clave "mensajes". \
      Paso 2: Identifica al cliente, que tendrá dentro de "mensajes", dentro de "response" y dentro de "author", el campo "guest". \
      Paso 3: Verifica si la última pregunta del cliente está dentro del contexto de la reserva o los pisos. \
      Paso 4: Si la pregunta está relacionada con el contexto, responde a la pregunta. En caso contrario, responde "No definido". \
      La respuesta debe ser breve y en lenguaje humano. \
      Aquí está todo el contexto de la situación: \
      {context}"""
          }]

  client = OpenAI(api_key=key)

  response = client.chat.completions.create(
      model="gpt-4",
      messages=prompt,
      temperature=0,
  )

  # Extract the content from the response
  content = response.choices[0].message.content

  # Obtener el número del destinatario de la tabla reservas
  #number = '+34601364570'

  #send_to_whatsapp(content,number)

  # If the content contains the detailed explanation, replace it with 'No definido'
  if "no definido" in content or "no especific" in content or "no se especifi" in content:
      content = 'No definido'
      msg = "Pregunta sin contexto recbidia"
      send_email(msg, recipient="alech.maria@hotmail.com", subject="Resultado de la prueba")

  return content




   

   
