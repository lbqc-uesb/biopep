from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import csv
import os

TIME_TO_WAIT = 10  # time to wait webdriver load page source in seconds


def submit(
    task_id: str,
    index: int,
    sequence: str,
    query_pdb: str,
    receptor: str,
    site: str,
):
    hpepdock = os.getenv("HPEPDOCK_URL", "http://huanglab.phys.hust.edu.cn/hpepdock/")
    path = f"{os.getcwd()}/output/{task_id}"

    if query_pdb:
        ligand = os.path.abspath(query_pdb)
    else:
        ligand = f"{path}/modelling/pep{index}/pep{index}.B99990001.pdb"

    if os.path.isfile(ligand):
        try:
            options = Options()
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--no-sandbox")
            options.add_argument("--headless")

            driver = Chrome(options=options)
            driver.set_page_load_timeout(TIME_TO_WAIT)

            driver.get(hpepdock)

            print("\nSubmitting docking to HPEPDOCK SERVER...")

            # receptor protein file path and peptide file path
            driver.find_element(By.ID, "pdbfile1").send_keys(os.path.abspath(receptor))
            driver.find_element(By.ID, "pdbfile2").send_keys(ligand)

            # advanced options
            driver.find_element(By.ID, "option1").click()
            driver.find_element(By.NAME, "sitenum1").send_keys(site)
            driver.find_element(By.NAME, "jobname").send_keys(f"pep{index}")

            # submit docking
            driver.find_element(
                By.XPATH, "/html/body/form/table/tbody/tr[8]/td/input[1]"
            ).click()

            # the link is required to see future results
            wait = WebDriverWait(driver, TIME_TO_WAIT, 1)
            wait.until(EC.url_changes(hpepdock))

            link = driver.current_url

            exists_submit_file = os.path.exists(f"{path}/out_submit.csv")
            with open(f"{path}/out_submit.csv", "a") as out_csv:
                csv_writer = csv.writer(out_csv, delimiter=",")
                if not exists_submit_file:
                    csv_writer.writerow(["Index", "Sequence", "Link"])
                csv_writer.writerow([index, sequence, link])

            print(f"\nDocking submitted to HPEPDOCK SERVER:\n   {link}")

        except Exception as error:
            with open(f"{path}/submit.log", "a") as log_csv:
                csv_writer = csv.writer(log_csv, delimiter=",")
                csv_writer.writerow(
                    [
                        f"{ligand}, ERROR: {error}",
                        f'{datetime.today().strftime("%Y-%m-%d %H:%M")}',
                    ]
                )
            print("\nError on submit docking to HPEPDOCK SERVER.")

        finally:
            if 'driver' in locals():
                driver.close()

    else:
        with open(f"{path}/submit.log", "a") as log_csv:
            csv_writer = csv.writer(log_csv, delimiter=",")
            csv_writer.writerow(
                [
                    f"{ligand} not found",
                    f'{datetime.today().strftime("%Y-%m-%d %H:%M")}',
                ]
            )
        print("\nLigand not found.\n")
