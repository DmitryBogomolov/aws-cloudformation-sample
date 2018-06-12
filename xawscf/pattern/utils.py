def get_full_name(name, root):
    return root.get('project') + '-' + name

def try_set_field(target, name, value):
    if value:
        target[name] = value

def make_output(value):
    return { 'Value': value }

def set_tags_list(template, resource):
    tags = [{ 'Key': key, 'Value': value } for key, value in resource.get('tags', {}).items()]
    template['Tags'].extend(tags)
