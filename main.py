import sys
from Bio import SeqIO
from Alpha.Search import Search
from Alpha.Modelling import Modelling
from Alpha.Docking import Docking
from Alpha.Scraping import Scraping
from output.output import Task


def execute(query, receptor, site, cut_off=30, task_name="task"):
    task = Task(task_name, query, receptor)
    for i, sequence in enumerate(SeqIO.parse(query, "fasta")):
        peptide = str(sequence.seq)
        print(f"Reading sequence{i}: {peptide}")
        if len(list(peptide)) <= cut_off:
            # Step 1 - Search homologous
            search = Search(task.id, i, peptide)
            search.createfasta()
            search.runblast()

            # Step 2 - Modelling
            modelling = Modelling(task.id, i, peptide, cut_off)
            modelling.run()

            # Step 3 - Docking
            docking = Docking(task.id, i, peptide, receptor, site)
            docking.submit()

        else:
            print(f"Sequence longer than {cut_off} amino acids.\n")
            continue

    print("Complete counterpart search.")
    print("Complete molecular modeling of peptides.")

    # Delete unmodeled peptides folders
    task.clear()

    # Get blast results
    print("Saving blast results...")
    task.blast()
    task.zip_pdbs()

    # Step 4 - Get docking results
    scraping = Scraping(task.id)
    scraping.start()

    print("Complete molecular docking of peptides.")

    task.finish()


if __name__ == "__main__":
    [_, query, receptor, site, cut_off, task_name] = sys.argv
    execute(query, receptor, site, int(cut_off), task_name)
