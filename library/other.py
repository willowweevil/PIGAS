import yaml


def read_yaml_file(input_file=None):
    with open(input_file, 'r', encoding="utf-8") as file:
        data = yaml.safe_load(file)
    return data