# coding: utf-8

import os
from Bio.Blast.Applications import NcbiblastpCommandline


class Search:
    def __init__(self, task_id, index, peptide):
        self.index = index
        self.peptide = peptide
        self.task_id = task_id

    def createfasta(self):
        pep_path = f"output/{self.task_id}/modelling/pep{self.index}"
        os.makedirs(pep_path)
        with open(f"{pep_path}/pep{self.index}.fasta", "a") as writing:
            writing.write(f">pep{self.index}\n")
            writing.write(self.peptide)

    def runblast(self):
        pep_path = f"output/{self.task_id}/modelling/pep{self.index}"
        command_blastp = NcbiblastpCommandline(
            task="blastp-short",
            query=f"{pep_path}/pep{self.index}.fasta",
            db="/blastdb/pdb_seqres",
            outfmt='"10 qseqid sseqid evalue bitscore pident qseq sseq qcovs"',
            out=f"{pep_path}/pep{self.index}.csv",
        )
        stdout, stderr = command_blastp()
