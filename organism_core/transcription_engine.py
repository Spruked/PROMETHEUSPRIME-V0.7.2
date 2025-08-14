from metaphor_biology import process_strand, simulate_mutagenesis
from nucleus_interface import retrieve_genomic_strand


def should_mutate(strand_id):
    # Placeholder: mutate 1 in 3 strands for demo
    import random
    return random.choice([True, False, False])


def trigger_cell_response(signal_config):
    activated_strands = []
    for strand_id in signal_config.get("transcribe_genome", []):
        strand = retrieve_genomic_strand(strand_id)
        if not strand:
            continue
        mutated_strand = simulate_mutagenesis(strand) if should_mutate(strand_id) else strand
        final_strand_id = process_strand(mutated_strand)
        if final_strand_id:
            activated_strands.append(final_strand_id)
    return activated_strands
