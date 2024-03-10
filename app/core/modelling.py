import os
import wget
import urllib
from modeller import *
from modeller.automodel import *
from datetime import datetime
import shutil


def run(task_id: str, index: int, sequence: str, min_pident=30):
    path = f"output/{task_id}"

    def __write_log(msg, show_code=True, cod=""):
        cod = f"{cod}," if show_code else ""
        with open(f"{path}/out.log", "a") as outfile:
            outfile.write(
                f"pep{index}, {sequence}, {cod} pident, {msg}, "
                f'{datetime.today().strftime("%Y-%m-%d %H:%M")}\n'
            )

    pep_path = f"{path}/modelling/pep{index}"
    with open(f"{pep_path}/pep{index}.csv", "r") as file:
        line = file.readline().split(",")
        try:
            code_pdb = line[1]
            pident = line[4]

            print(code_pdb, code_pdb[0:4], code_pdb[5:])

            if float(pident) >= min_pident:
                print(f"Homologous sequence found. Identity = {pident}\n")

                with open(f"{pep_path}/pep{index}.ali", "a") as writing:
                    writing.write(f">P1;pep{index}\n")
                    writing.write(f"sequence:pep{index}:::::::0.00: 0.00\n")
                    writing.write(f"{sequence}*")

                try:
                    link = f"https://files.rcsb.org/download/{code_pdb[0:4]}.pdb"
                    wget.download(link, pep_path)

                except (urllib.error.HTTPError, urllib.error.URLError):
                    print("urllib.error.HTTPError: HTTP Error 404: Not Found.")
                    __write_log(
                        "pdb file not found (download: error 404), unmodeled",
                        cod=code_pdb[0:4],
                    )

            else:
                __write_log("low identity, unmodeled", cod=code_pdb[0:4])

            if os.path.isfile(f"{pep_path}/{code_pdb[0:4]}.pdb"):
                try:
                    print("PDB file found.\n")
                    env = Environ()
                    aln = Alignment(env)
                    pdb = f"{pep_path}/{code_pdb[0:4]}"
                    mdl = Model(
                        env,
                        file=pdb,
                        model_segment=(
                            f"FIRST:{code_pdb[5]}",
                            f"LAST:{code_pdb[5]}",
                        ),
                    )
                    pdb_chain = f"{code_pdb[0:4]}{code_pdb[5]}"
                    aln.append_model(
                        mdl,
                        align_codes=pdb_chain,
                        atom_files=f"{pep_path}/{code_pdb[0:4]}.pdb",
                    )

                    file_ali = f"{pep_path}/pep{index}.ali"
                    code_ali = f"pep{index}"
                    aln.append(file=file_ali, align_codes=code_ali)
                    aln.align2d()

                    ali = f"{pep_path}/pep{index}-{pdb_chain}.ali"
                    aln.write(file=ali, alignment_format="PIR")

                    pap = f"{pep_path}/pep{index}-{pdb_chain}.pap"
                    aln.write(file=pap, alignment_format="PAP")

                    env = Environ()
                    a = AutoModel(
                        env,
                        alnfile=ali,
                        knowns=pdb_chain,
                        sequence=code_ali,
                        assess_methods=(
                            assess.DOPE,
                            assess.GA341,
                        ),
                    )
                    a.starting_model = 1
                    a.ending_model = 1
                    a.make()

                    # Move the modelling output files to output folder
                    output_models = [x for x in a.outputs if x["failure"] is None]
                    for om in output_models:
                        os.rename(om["name"], f"{pep_path}/{om['name']}")

                    exts = ["D00000001", "ini", "rsr", "sch", "V99990001"]
                    for ext in exts:
                        os.rename(
                            f"pep{index}.{ext}",
                            f"{pep_path}/pep{index}.{ext}",
                        )

                    __write_log("pdb file found, modeled", False)

                except ModellerError:
                    print("modeller.ModellerError")
                    __write_log(
                        "pdb file found, unmodeled (ModellerError)",
                        cod=code_pdb[0:4],
                    )

            else:
                print("PDB file not found.")
                __write_log("PDB file not found, unmodeled", False)

        except IndexError:
            print("Homologous not found.")
            __write_log("Homologous not found, unmodeled", False)


def get_peptides(task_id: str, modelled=True):
    peptides = {}
    with open(f"{os.getcwd()}/output/{task_id}/out.log") as submit_log:
        lines = submit_log.readlines()
        for line in lines:
            items = line.split(", ")
            if modelled and "unmodeled" not in line:
                peptides[items[0]] = items[1]
            elif not modelled and "unmodeled" in line:
                peptides[items[0]] = items[1]

    return peptides


def get_structures(task_id: str):
    output_task = f"./output/{task_id}"
    peptides = get_peptides(task_id)

    os.makedirs("structures", exist_ok=True)

    for pep in list(peptides.keys()):
        pdb_file = f"{output_task}/modelling/{pep}/{pep}.B99990001.pdb"
        os.system(f"cp {pdb_file} structures/{pep}.pdb")

    os.system(f"tar -czf {output_task}/structures.tar.gz structures")
    shutil.rmtree("structures")


def remove_empty_folders(task_id: str):
    peptides = get_peptides(task_id, modelled=False)
    for pep in list(peptides.keys()):
        pep_folder = f"{os.getcwd()}/output/{task_id}/modelling/{pep}"
        if os.path.exists(pep_folder):
            shutil.rmtree(pep_folder)
