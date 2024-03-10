import os
import sys
from app.utils import tasks
from Bio import SeqIO
from Bio.PDB import PDBParser
from Bio.SeqUtils import seq1
from app.core import blast, modelling, docking, scraping


def get_sequence_from_pdb(pdb_path: str):
    pdbparser = PDBParser()
    structure = pdbparser.get_structure("seq", pdb_path)
    [sequence] = [
        seq1("".join(residue.resname for residue in chain))
        for chain in structure.get_chains()
    ]

    return sequence


def get_query(input_type: str, query: str):
    if input_type == "Fasta":
        pdbs = None
        sequences = [str(sequence.seq) for sequence in SeqIO.parse(query, "fasta")]
    else:
        pdbs = [os.path.join(query, pdb) for pdb in os.listdir(query)]
        sequences = [get_sequence_from_pdb(pdb_file) for pdb_file in pdbs]

    return sequences, pdbs


def execute(
    option: str,
    query: str,
    cutoff: int,
    taskname: str,
    input_type: str,
    receptor: str,
    site: str,
):
    task = tasks.generate(option, query, cutoff, taskname, input_type, receptor, site)

    sequences, pdbs = get_query(input_type, query)

    run_option = {
        "Blast": input_type == "Fasta",
        "Modelling": option in ["Modelling", "Docking"] and input_type == "Fasta",
        "Docking": option == "Docking",
    }

    for index, sequence in enumerate(sequences):
        print(f"\nReading pep{index}: {sequence}")
        if len(sequence) <= cutoff:

            if run_option["Blast"]:
                blast.create_fasta(task["id"], index, sequence)
                blast.run(task["id"], index)

            if run_option["Modelling"]:
                modelling.run(task["id"], index, sequence)

            if run_option["Docking"]:
                query_pdb = pdbs[index] if pdbs else None
                docking.submit(task["id"], index, sequence, query_pdb, receptor, site)

        else:
            print(f"Sequence longer than {cutoff} amino acids.")
            continue

    if run_option["Blast"]:
        blast.get_results(task["id"])
        print("\nComplete counterpart blast search.")
        print(f"See results in: output/{task['id']}/blast.csv")

    if run_option["Modelling"]:
        modelling.remove_empty_folders(task["id"])
        modelling.get_structures(task["id"])
        print("\nComplete molecular modeling of peptides.")
        print(f"See modeled structures in: output/{task['id']}/structures.tar.gz")

    tasks.finish(task["id"])

    # Get docking results
    if run_option["Docking"]:
        scraping.start(task["id"])
        print("\nComplete molecular docking of peptides.")


if __name__ == "__main__":
    option = sys.argv[1]
    if option in ["Blast", "Modelling"]:
        [_, __, query, cutoff, taskname] = sys.argv
        input_type = "Fasta"
        receptor = None
        site = None
    elif option == "Docking":
        [_, __, input_type, query, receptor, site, cutoff, taskname] = sys.argv
    else:
        print("Invalid option")
        exit(1)

    execute(
        option=option,
        query=query,
        cutoff=int(cutoff),
        taskname=taskname,
        input_type=input_type,
        receptor=receptor,
        site=site,
    )
