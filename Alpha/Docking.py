# coding: utf-8

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from datetime import datetime

import csv
import os


TIME_TO_WAIT = 10 # time to wait webdriver load page source in seconds


class Docking:
    def __init__(self, task_id, index, peptide, receptor, site):
        self.peptide = peptide
        self.index = index
        self.receptor = f"{os.getcwd()}/{receptor}"
        self.site = site
        self.task_id = task_id
        self.hpepdock = os.getenv("HPEPDOCK_URL", "http://huanglab.phys.hust.edu.cn/hpepdock/")

    def submit(self):
        path = f"{os.getcwd()}/output/{self.task_id}"
        pep_path = f"{path}/modelling/pep{self.index}"
        ligand = f"{pep_path}/pep{self.index}.B99990001.pdb"

        if os.path.isfile(ligand):
            try:    
                options = Options()
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--no-sandbox")
                options.add_argument("--headless")

                driver = Chrome(options=options)
                driver.set_page_load_timeout(TIME_TO_WAIT)

                driver.get(self.hpepdock)

                # receptor protein file path and peptide file path
                driver.find_element(By.ID, "pdbfile1").send_keys(self.receptor)
                driver.find_element(By.ID, "pdbfile2").send_keys(ligand)

                # advanced options
                driver.find_element(By.ID, "option1").click()
                driver.find_element(By.NAME, "sitenum1").send_keys(self.site)
                driver.find_element(By.NAME, "jobname").send_keys(f"pep{self.index}")

                # submit docking
                driver.find_element(
                    By.XPATH, "/html/body/form/table/tbody/tr[8]/td/input[1]"
                ).click()

                # the link is required to see future results
                wait = WebDriverWait(driver, TIME_TO_WAIT, 1)
                wait.until(EC.url_changes(self.hpepdock))

                link = driver.current_url

                exists_submit_file = os.path.exists(f"{path}/out_submit.csv")
                with open(f"{path}/out_submit.csv", "a") as out_csv:
                    csv_writer = csv.writer(out_csv, delimiter=",")
                    if not exists_submit_file:
                        csv_writer.writerow(["Index", "Sequence", "Link"])
                    csv_writer.writerow([self.index, self.peptide, link])

            except:
                with open(f"{path}/submit.log", "a") as log_csv:
                    csv_writer = csv.writer(log_csv, delimiter=",")
                    csv_writer.writerow(
                        [
                            f"pep{self.index}.B99990001.pdb throw error on submit",
                            f'{datetime.today().strftime("%Y-%m-%d %H:%M")}',
                        ]
                    )
                print("\nError on submit docking to HPEPDOCK SERVER.\n")

            finally:
                driver.close()
                

        else:
            with open(f"{path}/submit.log", "a") as log_csv:
                csv_writer = csv.writer(log_csv, delimiter=",")
                csv_writer.writerow(
                    [
                        f"pep{self.index}.B99990001.pdb not found",
                        f'{datetime.today().strftime("%Y-%m-%d %H:%M")}',
                    ]
                )
            print("\nLigand not found.\n")

