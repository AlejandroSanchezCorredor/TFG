import json
import traceback
import http.client
from urllib.parse import urlparse
from datetime import datetime
from enum import Enum

from ..configuration_loader import get_configuration

class LogWebhookService(Enum):
    GOOGLE = "MONITOR_WEBHOOK_URL"
    SLACK = "SLACK_MONITOR_WEBHOOK_URL"

class WebhookTemplate():

    FORMAT_BOX = '`'
    FORMAT_BOLD = '*'
    FORMAT_CODE = '```'

    def template(self):
        return f'{self.section_environment()} \n\n' \
               f'{self.section_context()}\n\n' \
               f'{self.section_event()}\n\n' \
               f'{self.section_result()}'

    def section_environment(self):
        return f'{self._box("[ENVIRONMENT] {environment}")} ' \
               f'{self._box("[TYPE] {type}")} ' \
               f'{self._box("[DATETIME] {datetime}")}'

    def section_context(self):
        context_data = "aws_request_id: {aws_request_id} \n" \
                       "function_endpoint: {function_endpoint} \n" \
                       "function_name: {function_name} \n" \
                       "function_version: {function_version} \n" \
                       "log_group_name: {log_group_name} \n" \
                       "log_stream_name: {log_stream_name} \n" \
                       "log_cloudwatch_link: {log_cloudwatch_link}"


        return f'{self._box("[CONTEXT]")} \n' \
               f'{self._code(context_data)}'

    def section_event(self):
        return f'{self._box("[EVENT]")} \n' \
               f'{self._code("{event}")}'

    def section_result(self):
        return f'{self._box("[RESULT]")} \n' \
               f'{self._code("{result}")}'


    def _box(self, value):
        return f'{self.FORMAT_BOX}{value}{self.FORMAT_BOX}'

    def _bold(self, value):
        return f'{self.FORMAT_BOLD}{value}{self.FORMAT_BOLD}'

    def _code(self, value):
        return f'{self.FORMAT_CODE}{value}{self.FORMAT_CODE}'


def webhook_request(payload, service):
    config = get_configuration()

    METHOD = 'POST'
    HEADERS = {'Content-Type': 'application/json'}
    URL = getattr(config, service)
    PAYLOAD = json.dumps({"text": payload})

    conn = http.client.HTTPSConnection(urlparse(URL).netloc, timeout=0.75)
    conn.request(METHOD, URL, PAYLOAD, HEADERS)
    response = conn.getresponse()
    print("__WEBHOOK_RESPONSE__: ", response.read())


def webhook_send(request, exception):
    try:
        config = get_configuration()

        # Filter internal errors (not HTTPError)
        if not hasattr(exception, 'statusCode'):

            # Control local request (serverless offline)
            if request.context.__class__.__name__ != 'FakeLambdaContext':

                message = WebhookTemplate().template().format(
                    environment=getattr(config, "AWS_STAGE"),
                    datetime=datetime.utcnow(),
                    type=request.type,
                    aws_request_id=request.context.aws_request_id,
                    function_name=request.context.function_name,
                    function_version=request.context.function_version,
                    log_group_name=request.context.log_group_name,
                    log_stream_name=request.context.log_stream_name,
                    log_cloudwatch_link=_generate_link_cloudwatch_log(request.context),
                    # event=_filter_event_information(request.event),
                    event="<...>",
                    function_endpoint=f'[{request.event.get("httpMethod", "...")}] {request.event.get("resource", "")}',
                    result=''.join(traceback.format_exception(etype=type(exception), value=exception, tb=exception.__traceback__))
                )

                # Google Monitor > MESSAGE LIMIT: 4096 characters
                webhook_request(payload=message, service=LogWebhookService.GOOGLE.value)

                # Slack Monitor > MESSAGE LIMIT: 4000 characters https://api.slack.com/methods/chat.postMessage#truncating
                webhook_request(payload=message, service=LogWebhookService.SLACK.value)

    except Exception as e:
        print("__LAMBDA_ERROR__: ", exception)
        print("__WEBHOOK_ERROR__: ", e)
        pass


def _filter_event_information(event):
    _event = event

    try:
        # Remove info (to compact message)
        _event['headers']['x-amz-security-token'] = '<...>'
        _event['multiValueHeaders']['x-amz-security-token'] = '<...>'
        _event['headers']['Authorization'] = '<...>'
        _event['multiValueHeaders']['Authorization'] = '<...>'
        _event['requestContext']['identity'] = '<...>'
    except:
        return '...'

    return _event


def _generate_link_cloudwatch_log(context):
    config = get_configuration()

    try:
        link = f'https://{config.AWS_REGION}.console.aws.amazon.com/cloudwatch/home?region={config.AWS_REGION}#logsV2:log-groups' \
               f'/log-group/{context.log_group_name.replace("/", "$252F")}' \
               f'/log-events/{context.log_stream_name.replace("$", "$2524").replace("[", "$255B").replace("]", "$255D").replace("/", "$252F")}'
    except:
        return '<url_error>'

    return link

