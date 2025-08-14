from app import PrometheusPrime

input_data = {
    "trigger": "echo:legacy",
    "emotion": "reverence",
    "context": "user onboarding"
}

agent = PrometheusPrime()
output = agent.process(input_data)
print("Symbolic Output:", output)