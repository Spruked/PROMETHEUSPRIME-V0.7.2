from app import PrometheusPrime  # Adjust if needed

input_data = {
    "trigger": "echo:legacy",
    "emotion": "reverence",
    "context": "user onboarding"
}

agent = PrometheusPrime()
response = agent.process(input_data)
print("🜂 Trust Glyph Activated:", response)