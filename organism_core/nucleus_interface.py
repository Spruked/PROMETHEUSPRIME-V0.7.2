import os
import json

MANIFEST_PATH = os.path.join(os.path.dirname(__file__), "genome_manifest.json")


def load_genome_manifest():
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def retrieve_genomic_strand(strand_id):
    manifest = load_genome_manifest()
    for strand in manifest.get("example_strands", []):
        if strand["id"] == strand_id:
            strand_path = os.path.join(os.path.dirname(__file__), "..", strand["path"])
            if os.path.exists(strand_path):
                with open(strand_path, "r", encoding="utf-8") as f:
                    content = f.read()
                return {"id": strand_id, "metaphor": strand["metaphor"], "content": content}
            else:
                print(f"[strand_missing] {strand_id} expected at {strand_path}")
                return None
    print(f"[strand_not_found] {strand_id} not in manifest")
    return None
