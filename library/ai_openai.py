import openai
import logging
import time

def get_response(input_message):
    client = openai.OpenAI(
        api_key="sk-mbOK4BfoIlrsKFPzAe534e4506E34055815c582e6fFc270c",
        base_url="https://api.aiguoguo199.com/v1"
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # 4
            messages=[
                # {"role": "system", "content": context},
                {"role": "user", "content": input_message},
            ], temperature=0.7)
        return response.choices[0].message.content
    except openai.InternalServerError as e:
        logging.error(e)
        return None
