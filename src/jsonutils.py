def dump_details(obj):
    output = __dump_details_recursive(obj, "")
    if (output.endswith("\n")):
        output = output[:-len("\n")]
    return output


def __dump_details_dict(obj: dict, prefix: str):
    output = ""
    for key in obj:
        value = obj[key]
        new_prefix = prefix + '.' + key if prefix != "" else key
        
        # call recursive function
        output += __dump_details_recursive(value, new_prefix)
    return output


def __dump_details_list(obj: list, prefix: str):
    output = ""
    for i in range(len(obj)):
        key = "[{0}]".format(i) # this is how we refer to individual element in the list
        value = obj[i]
        new_prefix = prefix + key if prefix != "" else key
        
        # call recursive function
        output += __dump_details_recursive(value, new_prefix)
    return output


def __dump_details_recursive(obj, prefix: str):
    output = ""
    if (isinstance(obj, str)):
        output += prefix + ": '" + obj + "'\n"
    elif (isinstance(obj, bool)):
        value = "true" if obj else "false"
        output += prefix + ": " + value + "\n"
    elif (isinstance(obj, int) or isinstance(obj, float)):
        output += prefix + ": " + str(obj) + "\n"
    elif (isinstance(obj, list)):
        output += __dump_details_list(obj, prefix)
    elif (isinstance(obj, dict)):
        output += __dump_details_dict(obj, prefix)
    else:
        raise TypeError('Error unknown type of object for ' + prefix + ": " + str(type(obj)) )
    return output
