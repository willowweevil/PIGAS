import yaml
import openai
import logging
import os
import sys
import random


def is_debug(config_file):
    debug_level = False
    config = read_yaml_file(config_file)
    other_data = config.get('other')
    if other_data:
        debug_level = other_data.get('debug')
    return True if debug_level is True else False


def get_random(my_list):
    return random.choice(my_list)


def read_yaml_file(input_file=None):
    try:
        with open(input_file, 'r', encoding="utf-8") as file:
            data = yaml.safe_load(file)
    except FileNotFoundError:
        logging.error(f"File {input_file} not found.")
        sys.exit(1)
    except KeyboardInterrupt:
        logging.error(f"File \"{input_file}\" reading was interrupted by user.")
        sys.exit(0)
    return data


def get_open_ai_response(input_message):
    connection_parameters = read_yaml_file('config.yaml')
    client = openai.OpenAI(
        api_key=connection_parameters['open-ai']['api_key'],
        base_url=connection_parameters['open-ai']['base_url']
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": input_message},
            ], temperature=0.9)
        return response.choices[0].message.content
    except Exception as e:
        logging.error(e)
        return None


def read_the_context(context_file):
    if not os.path.exists(context_file):
        with open(context_file, 'w'):
            pass
    with open(context_file, 'r') as file:
        context = file.read()
        file.close()
    return context


def write_the_context(context_file, context):
    with open(context_file, "w", errors='ignore') as f:
        f.write(context)
        f.close()


def read_the_last_line(file):
    with open(file, 'r', errors='ignore') as f:
        lines = f.readlines()
        if len(lines) > 0:
            return lines[-1].strip()
        return None


def add_message_to_context(context_file, message):
    context = read_the_context(context_file)
    if message != read_the_last_line(context_file):
        context += f"\n{message}"
        write_the_context(context_file, context)


def clear_file(file_path):
    with open(file_path, 'r+') as file:
        file.truncate(0)
        file.close()
