from enum import Enum, auto


class RequestType(Enum):
    API_GATEWAY = auto()
    AUTHORIZER_TOKEN = auto()
    KEEP_WARM = auto()
    HTTP_KEEP_WARM = auto()
    AWS_EVENT_DYNAMODB = auto()
    AWS_EVENT_KINESIS = auto()
    AWS_EVENT_S3 = auto()
    AWS_EVENT_SNS = auto()
    AWS_EVENT_SQS = auto()
    AWS_EVENT_UNKNOWN = auto()
    UNKNOWN = auto()