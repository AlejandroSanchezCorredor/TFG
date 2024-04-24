from application.core.scheduler import SchedulerTasker
import datetime
from application.core.aws.ses import send_email

@SchedulerTasker.task('get_books')
def get_books(event, context): # Función con la que se obtendrán las reservas de la extranet de booking
    print("Obteniendo las reservas")
    #print("Prueba Scheduler")
    #today = datetime.datetime.now()
    #print("Hora actual:", today.strftime("%H:%M:%S"))

    # Captura la salida de print en una variable
    #output = ""
    #output += "Prueba Scheduler\n"
    #today = datetime.datetime.now()
    #output += f"Hora actual: {today.strftime('%H:%M:%S')}"

    #send_email(output, recipient="alech.maria@hotmail.com", subject="Resultado de la prueba")

    

