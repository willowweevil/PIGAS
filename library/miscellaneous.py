import yaml
import openai
import os
import sys
import time
import random
import logging

from yaml.parser import ParserError
from yaml.scanner import ScannerError

from library.errors import CommonError
from library.platforms import Platform

logging.basicConfig(level=logging.ERROR,
                    format="%(asctime)s %(levelname)s %(message)s")

for common_logger_name in logging.Logger.manager.loggerDict:
    logging.getLogger(common_logger_name).setLevel(logging.WARNING)


def setup_logging(loggers, debug=False):
    """
    Set up logging configuration for specified loggers with both console and
    file handlers. Allows for debug-level logging if specified.

    Args:
        loggers (list): A list of logger names to configure.
        debug (bool): Optional; Whether to enable debug-level logging. Defaults
            to False.

    """
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
    """
    Define the system platform based on the host operating system.

    Determines the platform on which the Python interpreter is
    running by evaluating the `sys.platform` value. It maps the platform to
    predefined `Platform` enum values such as LINUX, WINDOWS, or MACOS. If
    the platform cannot be recognized, an exception is raised.

    Returns:
        Platform: The platform corresponding to the current operating system.

    Raises:
        CommonError: If the platform cannot be identified from `sys.platform`.

    """
    if sys.platform in ['linux', 'linux2']:
        platform = Platform.LINUX
    elif sys.platform in ['Windows', 'win32', 'cygwin']:
        platform = Platform.WINDOWS
    elif sys.platform in ['Mac', 'darwin', 'os2', 'os2emx']:
        platform = Platform.MACOS
    else:
        raise CommonError(f"Cannot define platform: {sys.platform}")
    # logging.debug(f"System platform was defined as {str(platform).split('.')[1]}.")
    return platform


def stop_execution(code, input_message="\nPress Enter to exit...\n"):
    """
    Stop the program execution with an optional exit code and a customizable input message
    according to platform.

    """
    time.sleep(0.5)
    platform = define_system_platform()
    if platform == Platform.WINDOWS:
        try:
            input(input_message)
        except KeyboardInterrupt:
            pass
    sys.exit(code)


def unexpected_finish(e, title=None, traceback=None):
    """
    Handles unexpected termination of the program by logging the error and stopping execution.

    """
    if title:
        e = ': '.join([title, str(e)])
    if traceback:
        e = '\n'.join([e, traceback])
    logging.error(e)
    stop_execution(1)


def is_debug(config_file):
    """
    Determine whether the program is running in debug mode based on the configuration file.

    """
    debug_level = False
    config = read_yaml_file(config_file, critical=True)
    other_data = config.get('other')
    if other_data:
        debug_level = other_data.get('debug')
    return True if debug_level is True else False


# def debug_pressed_keys(config_file):
#     debug_level = False
#     config = read_yaml_file(config_file)
#     other_data = config.get('other')
#     if other_data:
#         debug_level = other_data.get('pressed_keys')
#     return True if debug_level is True else False

def get_random(my_list):
    """
    Get a random element from a list.

    """
    return random.choice(my_list)


def read_yaml_file(input_file=None, critical=False):
    """
    Read and parse a YAML file.

    Opens and reads a YAML file from the provided input path. It uses
    safe parsing to convert YAML content into Python objects. If the file is not
    found and the critical parameter is set to True, an exception is raised. It also handles
    errors caused by incorrect YAML formatting or indentation.

    Args:
        input_file (str or None): Path to the YAML file to be read. Defaults to None.
        critical (bool): Flag indicating whether the operation is critical. If True,
            raises an exception if the file is not found. Defaults to False.

    Returns:
        dict or None: Parsed content of the YAML file as a dictionary. Returns None
        if the file is not found and critical is False.

    Raises:
        CommonError: If the YAML file is not found and critical is True, or if the
        file contains errors during parsing.
    """
    try:
        with open(input_file, 'r', encoding="utf-8") as file:
            data = yaml.safe_load(file)
    except FileNotFoundError:
        if critical:
            # logging.error(f"File {input_file} not found.")
            raise CommonError(f"File {input_file} not found.")
        return None
    except (ScannerError, ParserError) as e:
        exception_text = str(e).replace('\n', ' ').replace('   ', ' ')
        raise CommonError(f"Incorrect {input_file} file! Error: {exception_text}.\n"
                          f"Please, be sure that indentation is correct (two spaces per level).")
    # except KeyboardInterrupt:
    #     logging.error(f"File \"{input_file}\" reading was interrupted by user.")
    return data


def get_open_ai_connection_parameters():
    """
    Fetches the OpenAI connection parameters from a configuration file.

    Reads the 'open-ai.yaml' configuration file to retrieve the API key and base
    URL required for accessing the OpenAI API. If the file is not found or the
    required parameters are missing, appropriate warnings are logged and default
    values are returned as None.

    Returns:
        dict: A dictionary containing 'api_key' and 'base_url' keys. Both values
        may be None if not specified in the configuration file or if the file
        is missing.
    """
    open_ai_config_file = 'open-ai.yaml'
    open_ai_config = read_yaml_file(open_ai_config_file)
    if open_ai_config:
        api_key = open_ai_config.get('api_key', None)
        base_url = open_ai_config.get('base_url', None)
        if not api_key:
            logging.warning(f'OpenAI API Key not found. Please, check the \"{open_ai_config_file}\" file.')
        if not base_url:
            logging.warning(f'OpenAI API URL not found. Please, check the \"{open_ai_config_file}\" file.')
    else:
        api_key, base_url = None, None
        logging.warning(f"{open_ai_config_file} not found.")

    return {'api_key': api_key, 'base_url': base_url}


def get_open_ai_response(input_message):
    """
    Generates a response from OpenAI's language model based on the provided input message.

    Establishes a connection to the OpenAI API using predefined
    connection parameters, sends the input message to the model, and retrieves
    the response. If an error occurs during the interaction with the OpenAI API,
    the function logs the error and returns None.

    Parameters:
        input_message (str): The input message to be sent to the OpenAI model.

    Returns:
        str | None: The content of the response from the language model if successful,
        otherwise None.
    """
    connection_params = get_open_ai_connection_parameters()
    try:
        client = openai.OpenAI(
            api_key=connection_params['api_key'],
            base_url=connection_params['base_url'],
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
