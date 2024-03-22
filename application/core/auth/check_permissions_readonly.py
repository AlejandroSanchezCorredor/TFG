from application.core.aws.cognito import authorizer_get_data
from application.core.configuration_loader import get_configuration
from application.core.http import HTTPError

class CheckReadOnly(object):
    def __call__(self, orig_func):
        def wrapper(*args, **kwargs):
            if args:
                configuration = get_configuration()
                cognito_groups = authorizer_get_data(args[0], 'cognito:groups')
                if cognito_groups and configuration.COGNITO_FULL_READ_ONLY_GROUP in cognito_groups:
                    print(cognito_groups)
                    raise HTTPError(401, 'Not Authorized, the user belongs to read-only group')
            return orig_func(*args, **kwargs)

        return wrapper

class CheckRoiReadOnly(object):
    def __call__(self, orig_func):
        def wrapper(*args, **kwargs):
            if args:
                configuration = get_configuration()
                cognito_groups = authorizer_get_data(args[0], 'cognito:groups')
                if cognito_groups and configuration.COGNITO_ROI_READ_ONLY_GROUP in cognito_groups:
                    raise HTTPError(401, 'Not Authorized, the user belongs to roi-read-only group')
            return orig_func(*args, **kwargs)

        return wrapper