import os
from openai import OpenAI
from twilio.rest import Client
import json


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
  
  json_str = json.dumps(message)
  
  key = os.getenv('CHATGPT_API_KEY', None)

  prompt = [{'role':'system', 'content':"""You are an assistant that responds to questions automatically. \
    Your task is to answer customers' questions about the flats. \
    To do this, follow these steps: \
    Step 1: Identify the name of each flat in a JSON. \
    Step 2: Identify the "conversation" field in each flat and within it, the "content" field. \
    Step 3: Find the last question asked by a sender and respond to that question or query. \
    Keep in mind that you should not respond to questions that you have already answered before. \
    For example: "content": "Sender: Hi, what are the usual ratings for this flat? \
    \nReceiver: The average is 7.8. \nSender: What is the location of the flat? \
    \nReceiver: Stone Street. \n Sender: Is the flat available?" \
    In the previous case, the only unanswered question is "Is the flat available?" \
    You should respond to that question. \
    Step 4: Provide the response in JSON format, for example: \
    {
    "Flat_name": "Response_to_question",
    } \
    
    Keep in mind that there will be content in "content". \
    Here's all the contextual information for the situation: \
     """ + json_str + """
    
    """}]

  client = OpenAI(api_key=key)

  response = client.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=prompt,
      temperature=0,
  )

  # Obtener el número del destinatario de la tabla reservas
  number = '+34601364570'

  send_to_whatsapp(response.choices[0].message.content,number)

  return response.choices[0].message.content




   

   
