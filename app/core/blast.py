import os
from Bio.Blast.Applications import NcbiblastpCommandline
from app.utils import tasks
import pandas as pd
from Bio import SeqIO
import numpy as np


def create_fasta(task_id, index, sequence):
    pep_path = f"output/{task_id}/modelling/pep{index}"
    os.makedirs(pep_path)
    with open(f"{pep_path}/pep{index}.fasta", "a") as writing:
        writing.write(f">pep{index}\n")
        writing.write(sequence)


def run(task_id, index):
    pep_path = f"output/{task_id}/modelling/pep{index}"
    command_blastp = NcbiblastpCommandline(
        task="blastp-short",
        query=f"{pep_path}/pep{index}.fasta",
        db="/blastdb/pdb_seqres",
        outfmt='"10 qseqid sseqid evalue bitscore pident qseq sseq qcovs"',
        out=f"{pep_path}/pep{index}.csv",
    )
    command_blastp()


def get_results(task_id: str):
    output_task = f"{os.getcwd()}/output/{task_id}"

    if not os.path.exists(f"{output_task}/modelling"):
        return

    peptides = os.listdir(f"{output_task}/modelling")

    pep_dfs = []
    for pep in peptides:
        # check if csv file is empty
        if os.stat(f"{output_task}/modelling/{pep}/{pep}.csv").st_size == 0:
            continue

        [sequence] = SeqIO.parse(f"{output_task}/modelling/{pep}/{pep}.fasta", "fasta")

        df = pd.read_csv(f"{output_task}/modelling/{pep}/{pep}.csv", header=None)
        df = pd.concat([df, pd.Series(np.full(len(df), str(sequence.seq)))], axis=1)
        pep_dfs.append(df)

    df = pd.concat(pep_dfs, ignore_index=True)
    df.columns = [
        "qseqid",
        "sseqid",
        "evalue",
        "bitscore",
        "pident",
        "qseq",
        "sseq",
        "qcovs",
        "sequence",
    ]

    df = df.reindex(
        [
            "qseqid",
            "sseqid",
            "sequence",
            "evalue",
            "bitscore",
            "pident",
            "qcovs",
            "qseq",
            "sseq",
        ],
        axis=1,
    )

    df.to_csv(f"{output_task}/blast.csv", index=False)
