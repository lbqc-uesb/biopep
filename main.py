import sys
from Bio import SeqIO
from Alpha.Biopep import Peptide
from Alpha.Modelling import Modelling
from Alpha.Submit import Dock
from output import output
import dock_scraping as ds


def execute(query, receptor, site, cut_off=30, task="task"):
    output.generate(task, query, receptor)
    for i, sequence in enumerate(SeqIO.parse(query, "fasta")):
        print(f"Reading sequence{i}: {sequence.seq}")
        if len(list(str(sequence.seq))) <= cut_off:
            # Step 1 - Search homologous
            search = Peptide(i, str(sequence.seq))
            search.createfasta()
            search.runblast()

            # Step 2 - Modelling
            modeller = Modelling(i, str(sequence.seq), cut_off)
            modeller.run_modelling()

            # Step 3 - Docking
            dock = Dock(i, str(sequence.seq), receptor, site)
            dock.submit()

        else:
            print(f"Sequence longer than {cut_off} amino acids.\n")
            continue

    print("Complete counterpart search.")
    print("Complete molecular modeling of peptides.")

    # Delete unmodeled peptides folders
    output.clear()

    # Get blast results
    print("Saving blast results...")
    output.blast()
    output.zip_pdbs()

    # Step 4 - Get docking results
    ds.start_scraping()

    print("Complete molecular docking of peptides.")

    output.finish()


if __name__ == "__main__":
    [_, query, receptor, site, cut_off, task] = sys.argv
    execute(query, receptor, site, int(cut_off), task)
