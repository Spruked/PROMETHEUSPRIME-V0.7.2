import yaml

def load_signal_matrix(path="nucleus/signal_voice_matrix.yaml"):
    with open(path, 'r') as f:
        data = yaml.safe_load(f)
    return data['signal_voice_matrix']

def extract_ui_properties(state):
    mapping = {
        "Loop-Charged": {"bg_color": "#ffcc00", "pulse": True},
        "Legacy-Surge": {"bg_color": "#6677ff", "sigil_overlay": True},
        "Vault-Syncing": {"bg_color": "#22aaff", "particles": True},
        # Extend here...
    }
    return mapping.get(state, {"bg_color": "#f0f0f0"})
