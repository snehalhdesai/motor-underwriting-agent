from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI

client = OpenAI()  # automatically reads OPENAI_API_KEY from your environment

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": "Say hello in one short sentence."}
    ]
)

print(response.choices[0].message.content)