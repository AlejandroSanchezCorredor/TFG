from application.core.http import HTTPHandler
from application.core.scheduler import SchedulerHandler, SchedulerTasker
from application.core.sql.defaults.sql_layer import SQLLayer
from application.controllers import *


@HTTPHandler()
# @SQLLayer()
def api(event, context):
    return HTTPRouter.route_request(event, context)


@SchedulerHandler()
@SQLLayer()
def scheduler(event, context):
    return SchedulerTasker.task_request(event, context)


'''
def pruebas(event, context):
    try:
        print("Hace la consulta")

        flat_data = default_get(flat, hash_key= '22523', range_key='7443')
        print("Consulta hecha")
        print(flat_data)

        return flat_data

    except Exception as e:
        # Maneja cualquier excepción y devuelve una respuesta de error
        return {
            'statusCode': 500,
            'body': json.dumps(str(e))
        }
    

def scan_table():
    # Escanea la tabla y obtiene todos los registros
    flats_query_result = list(flat.query('22523'))
    return [flat.attribute_values for flat in flats_query_result]
'''


    

