import random

metaphor_ledger = []

BIO_METAPHOR_CONTEXT = "biological"


def record_metaphor_event(strand_id, original_context, target_context, status, notes=""):
    event = {
        "strand_id": strand_id,
        "from": original_context,
        "to": target_context,
        "status": status,
        "notes": notes
    }
    metaphor_ledger.append(event)
    print(f"[metaphor_event] {event}")


def metaphor_adapter(strand, target_context: str = BIO_METAPHOR_CONTEXT):
    original_context = strand.get("metaphor", "unknown")
    strand_id = strand.get("id", "unknown")

    if original_context == target_context:
        record_metaphor_event(strand_id, original_context, target_context, "native")
        return strand

    if original_context == "ritual" and target_context == "biological":
        strand["metaphor"] = target_context
        record_metaphor_event(strand_id, original_context, target_context, "adapted", "Translated from ritual syntax.")
        return strand

    record_metaphor_event(strand_id, original_context, target_context, "rejected", "Untranslatable context.")
    return None


def process_strand(strand, metaphor_context: str = BIO_METAPHOR_CONTEXT):
    strand_id = strand.get("id", "unknown")
    if strand.get("metaphor") != metaphor_context:
        print(f"[strand_misalignment] Strand {strand_id} is metaphorically incompatible.")
        adapted = metaphor_adapter(strand, metaphor_context)
        if not adapted:
            print(f"[strand_rejection] Strand {strand_id} could not be adapted.")
            return None
        strand = adapted
    print(f"Strand {strand_id} accepted and activated.")
    return strand_id


def simulate_mutagenesis(strand, context_pool=["biological", "ritual", "neural"]):
    strand_id = strand.get("id", "unknown")
    current_context = strand.get("metaphor", "unknown")
    mutation_target = random.choice([ctx for ctx in context_pool if ctx != current_context])
    strand["metaphor"] = mutation_target
    record_metaphor_event(strand_id, current_context, mutation_target, "mutated", "Random metaphor mutation.")
    return strand
