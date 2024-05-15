from twilio.rest import Client

def send_to_whatsapp(gpt_response,number): # Enviamos por whatsapp la respuesta generada por ChatGPT al cliente
  from_whatsapp_number='whatsapp:+14155238886'
  # from_sms_number='+15677043718'

  client = Client("Credencial1", "Credencial2") 

  message = client.messages.create(
  from_= from_whatsapp_number,
  body=gpt_response,
  to= number # Obtendríamos el número del cliente de la tabla donde almacenamos las reservas
  )