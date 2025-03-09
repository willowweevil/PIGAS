import yaml
import openai
import logging

def read_yaml_file(input_file=None):
    with open(input_file, 'r', encoding="utf-8") as file:
        data = yaml.safe_load(file)
    return data

def get_response(input_message):
    connection_parameters = read_yaml_file('config.yaml')
    client = openai.OpenAI(
        api_key="sk-mbOK4BfoIlrsKFPzAe534e4506E34055815c582e6fFc270c",
        base_url="https://api.aiguoguo199.com/v1"
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": input_message},
            ], temperature=0.9)
        return response.choices[0].message.content
    except openai.InternalServerError as e:
        logging.error(e)
        return None
