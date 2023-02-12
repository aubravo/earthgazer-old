def config_bool(value: str):
    if isinstance(value, str):
        if value.lower() in ("yes", "true", "1"):
            return True
        elif value == '':
            return None
    elif value is None:
        return None
    else:
        raise TypeError('value should be an instance of \'str\'.')


def config_int(value: str):
    if isinstance(value, str):
        if value == '':
            return None
        else:
            return int(value)
    elif value is None:
        return None
    else:
        raise TypeError('value should be an instance of \'str\'.')


def config_float(value: str):
    if isinstance(value, str):
        if value == '':
            return None
        else:
            return float(value)
    elif value is None:
        return None
    else:
        raise TypeError('value should be an instance of \'str\'.')
