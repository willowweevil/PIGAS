import yaml
import openai
import logging

def read_yaml_file(input_file=None):
    with open(input_file, 'r', encoding="utf-8") as file:
        data = yaml.safe_load(file)
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

