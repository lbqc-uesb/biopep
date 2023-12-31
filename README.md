# BioPep

> Pipeline for the search of homologues and molecular modeling for each peptide as well as the molecular docking between the peptides and the RBD receptor (PDB: 6LZG) of SARS-CoV-2.
>> By Lucas Palmeira: CNPq Technological Initiation Scholarship | Data Scientist in Training <br>
>> By William Sena: CNPq Technological Initiation Scholarship | Python Developer

## Licence
> GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007

## Requisites

- A [Modeller](https://salilab.org/modeller/) License Key;
- System Operational with [Docker](https://www.docker.com) installed;

## Download

Download biopep source code:
```bash
curl -L https://github.com/lbqc-uesb/biopep/archive/refs/tags/v2.0.tar.gz -o biopep.tar.gz
```

Unzip files:
```bash
tar -xzf biopep.tar.gz
```

Navigate to biopep folder:
```bash
cd biopep-2.0
```

## Installation

Export biopep to path
```bash
export BIOPEP_PATH="$(pwd)"
export PATH="$PATH:$BIOPEP_PATH/bin"
```

Run installer script
```bash
biopep install
```

## Run

Execute BioPep:
```bash
biopep run
```
or
```bash
biopep run -q {QUERY} -r {RECEPTOR} -s {SITE}
```
or
```bash
biopep run -q {QUERY} -r {RECEPTOR} -s {SITE} -t {TASK} -c {CUT OFF}
```

### Options:
- `-q` | **QUERY**: query sequences file (.fasta, example: "*/home/myuser/query.fasta*")
- `-r` | **RECEPTOR**: receptor file (.pdb, example: "*/home/myuser/receptor.pdb*")
- `-s` | **SITE**: binding site (example: "*455:B, 486:B, 493:B, 501:B*")
- `-c` | **CUT-OFF**: max length of sequence (default: 30)
- `-t` | **TASK**: taskname to results folder (default: "*task*")

## Please, cite:
> ### BioPep
> Lucas Sousa Palmeira, & William Sena. (2021). BioPep. Zenodo. https://doi.org/10.5281/zenodo.5781778

> ### Hpepdock:
> ZHOU, Pei; JIN, Bowen; LI, Hao; et al. HPEPDOCK: A web server for blind peptide-protein acoplamento based on a hierarchical algorithm. Nucleic Acids Research, v. 46, n. W1, p. W443–W450, 2018.

> ### Modeller:
> ŠALI, Andrej; BLUNDELL, Tom L. Comparative protein modelling by satisfaction of spatial restraints. Journal of Molecular Biology, v. 234, n. 3, p. 779–815, 1993.
> 
> WEBB, Benjamin; SALI, Andrej. Comparative Protein Structure Modeling Using MODELLER. Current protocols in bioinformatics, v. 54, p. 5.6.1-5.6.37, 2016.

> ### Blast:
> CAMACHO, Christiam; COULOURIS, George; AVAGYAN, Vahram; et al. BLAST+: architecture and applications. BMC Bioinformatics, v. 10, p. 421, 2009.

> ### APD3: The antimicrobial peptide database
> WANG, Guangshun; LI, Xia; WANG, Zhe. APD3: The antimicrobial peptide database as a tool for research and education. Nucleic Acids Research, v. 44, n. D1, p. D1087–D1093, 2016.
