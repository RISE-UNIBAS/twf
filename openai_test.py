from twf.clients.simple_ai_clients import AiApiClient

client = AiApiClient('openai', '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')
answer, elapsed_time = client.prompt(
    model="gpt-4o",
    prompt=f"Describe 'Hamburg' in a few sentences."
)
print(answer.choices[0].message.to_json())
