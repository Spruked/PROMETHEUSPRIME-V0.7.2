import yaml

with open("cali/config/ethics.yaml", "r") as f:
    ethics_config = yaml.safe_load(f)

# Example: print loaded config for verification
def print_ethics_config():
    import pprint
    pprint.pprint(ethics_config)

if __name__ == "__main__":
    print_ethics_config()
