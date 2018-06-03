def try_set_field(target, name, value):
    if value:
        target[name] = value

def sanitize_resource_name(name):
    return name.title().replace('-', '').replace('_', '')

def make_output(value):
    return { 'Value': value }

def set_tags_list(template, resource):
    tags = [{ 'Key': key, 'Value': value } for key, value in resource.get('tags', {}).items()]
    template['Tags'].extend(tags)

def set_sub_list(target, resource, field, SubResouce):
    target.extend([SubResouce(obj).dump() for obj in resource.get(field, [])])
