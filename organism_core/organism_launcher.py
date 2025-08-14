
from transcription_engine import trigger_cell_response
from metaphor_biology import simulate_mutagenesis, process_strand
from nucleus_interface import retrieve_genomic_strand
from genome_scanner import scan_genome_folder

# 🧠 Signal Configuration
activation_signal = {
    "transcribe_genome": [
        "epistemology-core",
        "ritual-strand-A",
        "neural-strand-B"
    ],
    "synaptic_echo": [
        "🧠 Memory nucleus initialized.",
        "🌱 Genomic pulse distributed.",
        "⚡ Transcription network activated."
    ]
}

ENABLE_MUTAGENESIS = True
RUN_GENOME_SCAN = True

def initiate_organism_cycle():
    print("\n🚀 Organism awakening initiated...\n")

    # 🧬 Full Genome Audit
    if RUN_GENOME_SCAN:
        scan_genome_folder(adapt_if_needed=True)

    # � Strand Preparation
    strand_pool = []
    for strand_id in activation_signal.get("transcribe_genome", []):
        strand = retrieve_genomic_strand(strand_id)
        if strand:
            if ENABLE_MUTAGENESIS:
                strand = simulate_mutagenesis(strand)
            result = process_strand(strand)
            if result:
                strand_pool.append(result)

    # 🧠 Feedback Signals
    for signal in activation_signal.get("synaptic_echo", []):
        print(signal)

    print(f"\n✅ Transcription complete. Activated strands: {strand_pool}\n")

if __name__ == "__main__":
    initiate_organism_cycle()
