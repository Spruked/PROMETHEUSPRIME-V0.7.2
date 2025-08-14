import os
import json
from metaphor_biology import metaphor_adapter, record_metaphor_event

GENOME_FOLDER = "nucleus/genome_strands"
TARGET_METAPHOR = "biological"

def scan_genome_folder(folder_path=GENOME_FOLDER, adapt_if_needed=True):
    compliant_strands = []
    for filename in os.listdir(folder_path):
        if not filename.endswith(".json"):
            continue

        path = os.path.join(folder_path, filename)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                strand = json.load(f)
                strand_id = strand.get("id", filename)
                metaphor = strand.get("metaphor", "unknown")

                if metaphor != TARGET_METAPHOR:
                    print(f"[audit] Strand {strand_id} not compliant.")
                    if adapt_if_needed:
                        adapted = metaphor_adapter(strand, TARGET_METAPHOR)
                        if adapted:
                            with open(path, 'w', encoding='utf-8') as fw:
                                json.dump(adapted, fw, indent=2)
                            print(f"[adapted] Strand {strand_id} updated.")
                    else:
                        record_metaphor_event(strand_id, metaphor, TARGET_METAPHOR, "noncompliant")
                else:
                    compliant_strands.append(strand_id)
                    record_metaphor_event(strand_id, metaphor, TARGET_METAPHOR, "native")
        except Exception as e:
            print(f"[error] Failed to process {filename}: {e}")

    print(f"\n🧠 Genome scan complete. {len(compliant_strands)} strands aligned.\n")
    return compliant_strands
