# Summary actions permission in single dict
# a) role > modules > permissions
# b) user > modules > permisisons
def reduce_permissions(user):
    access = {'role': {'id': None, 'name': None, 'modules': []}, 'policy': {'modules': []}}

    if user:
        # Include role permissions
        for _access in user.role.access:
            access.update({'role': {'id': _access.role.id, 'name': _access.role.name, 'modules': access['role']['modules']}})

            _module = next((m for m in access['role']['modules'] if m['code'] == _access.module.code), None)

            if _module is None:
                access['role']['modules'].append(
                    {'code': _access.module.code, 'path': _access.module.path, 'permissions': [_access.permission.code]}
                )
            else:
                _module['permissions'].append(_access.permission.code)

        # Include user permissions from policies
        for _policy in user.policies:
            access.update({'policy': {'modules': access['policy']['modules']}})

            _module = next((m for m in access['policy']['modules'] if m['code'] == _policy.module.code), None)

            if _module is None:
                access['policy']['modules'].append(
                    {'code': _policy.module.code, 'path': _policy.module.path, 'permissions': [_policy.permission.code]}
                )
            else:
                _module['permissions'].append(_policy.permission.code)

    return access


def summary_role_permissions(role):
    access = {'id': role.id, 'name': role.name, 'modules': []}

    if role:
        for _access in role.access:
            access.update({'modules': access['modules']})

            _module = next((m for m in access['modules'] if m['code'] == _access.module.code), None)

            if _module is None:
                access['modules'].append({
                    'name': _access.module.name, 'path': _access.module.path,
                    'code': _access.module.code, 'description': _access.module.description,
                    'permissions': [_access.permission.code]
                })
            else:
                _module['permissions'].append(_access.permission.code)

    return access


def summary_policy_permissions(user):
    policy = {'id': user.id, 'email': user.email, 'modules': []}

    if user:
        for _policy in user.policies:
            policy.update({'modules': policy['modules']})

            _module = next((m for m in policy['modules'] if m['code'] == _policy.module.code), None)

            if _module is None:
                policy['modules'].append({
                    'name': _policy.module.name, 'path': _policy.module.path,
                    'code': _policy.module.code, 'description': _policy.module.description,
                    'permissions': [_policy.permission.code]
                })
            else:
                _module['permissions'].append(_policy.permission.code)

    return policy