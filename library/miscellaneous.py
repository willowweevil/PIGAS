import yaml
import openai
import os
import sys
import time
import random
import logging

from library.errors import CommonError
from library.platforms import Platform

logging.basicConfig(level=logging.ERROR,
                    format="%(asctime)s %(levelname)s %(message)s")

def setup_logging(loggers, debug=False):
    # Clear any existing handlers (important to avoid duplicates)
    logging.root.handlers = []

    # Create formatter
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

    # --- Console Handler (STDOUT) ---
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG if debug else logging.INFO)

    # --- File Handler (main.log) ---
    file_handler = logging.FileHandler("pigas.log", mode='w')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG if debug else logging.INFO)

    # Apply to root logger (captures all modules)
    logging.root.setLevel(logging.DEBUG)  # Set to the lowest level (handlers filter further)
    logging.root.addHandler(console_handler)
    logging.root.addHandler(file_handler)

    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG if debug else logging.INFO)
        logger.propagate = True

def define_system_platform():
    if sys.platform in ['linux', 'linux2']:
        platform = Platform.LINUX
    elif sys.platform in ['Windows', 'win32', 'cygwin']:
        platform = Platform.WINDOWS
    elif sys.platform in ['Mac', 'darwin', 'os2', 'os2emx']:
        platform = Platform.MACOS
    else:
        raise CommonError(f"Cannot define platform: {sys.platform}")
    #logging.debug(f"System platform was defined as {str(platform).split('.')[1]}.")
    return platform

def stop_execution(code, input_message="\nPress Enter to exit...\n"):
    time.sleep(0.5)
    platform = define_system_platform()
    if platform == Platform.WINDOWS:
        try:
            input(input_message)
        except KeyboardInterrupt:
            pass
    sys.exit(code)

def unexpected_finish(e, title=None, traceback=None):
    if title:
        e = ': '.join([title, str(e)])
    if traceback:
        e = '\n'.join([e, traceback])
    logging.error(e)
    stop_execution(1)

def is_debug(config_file):
    debug_level = False
    config = read_yaml_file(config_file)
    other_data = config.get('other')
    if other_data:
        debug_level = other_data.get('debug')
    return True if debug_level is True else False

def debug_pressed_keys(config_file):
    debug_level = False
    config = read_yaml_file(config_file)
    other_data = config.get('other')
    if other_data:
        debug_level = other_data.get('pressed_keys')
    return True if debug_level is True else False

def get_random(my_list):
    return random.choice(my_list)


def read_yaml_file(input_file=None):
    try:
        with open(input_file, 'r', encoding="utf-8") as file:
            data = yaml.safe_load(file)
    except FileNotFoundError:
        logging.error(f"File {input_file} not found.")
        stop_execution(1)
    # except KeyboardInterrupt:
    #     logging.error(f"File \"{input_file}\" reading was interrupted by user.")
    return data


def get_open_ai_response(input_message):
    connection_parameters = read_yaml_file('config.yaml')
    try:
        client = openai.OpenAI(
            api_key=connection_parameters['open-ai']['api_key'],
            base_url=connection_parameters['open-ai']['base_url']
        )
    except openai.OpenAIError as e:
        logging.error(e)
        return None
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
