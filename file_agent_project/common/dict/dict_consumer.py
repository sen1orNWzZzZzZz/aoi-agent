
def get_nested_value(data_dict, path_str, separator='.'):
    """
    通过路径字符串获取嵌套字典的值
    例如: path="user.profile.name" -> dict["user"]["profile"]["name"]
    """
    keys = path_str.split(separator)
    value = data_dict
    
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return None  # 或抛出 KeyError
    return value

def set_nested_value(data_dict, path_str, value, separator='.'):
    """
    更新嵌套字典指定路径的值，自动创建不存在的中间层级
    """
    keys = path_str.split(separator)
    current = data_dict
    
    # 遍历除最后一个key外的所有key
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    
    # 设置最终值
    current[keys[-1]] = value
    return data_dict