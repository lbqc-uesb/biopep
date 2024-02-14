from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import pandas as pd
import time
import wget
import os


RELOAD_TIME = 120 # time to reload results page in seconds
TIME_TO_WAIT = 10 # time to wait webdriver in seconds


class Scraping:
    def __init__(self, task_id):
        self.task_id = task_id

    def start(self):
        out_path = f"{os.getcwd()}/output/{self.task_id}"
        df = pd.read_csv(f"{out_path}/out_submit.csv")

        items = items_copy = [
            {
                "Index": row["Index"],
                "Sequence": row["Sequence"],
                "Link": row["Link"],
                "Energy": "NaN",
                "Status": "NONE",
            }
            for i, row in df.iterrows()
        ]

        print("\nStarting docking scraping...")
        print(
            f"It's will try to do the docking scraping every {RELOAD_TIME} seconds.\n",
            flush=True,
        )

        while len(items) > 0:
            options = Options()
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--no-sandbox")
            options.add_argument("--headless")

            driver = Chrome(options=options)
            driver.set_page_load_timeout(TIME_TO_WAIT)

            for item in items:
                try:
                    driver.get(item["Link"])

                    wait = WebDriverWait(driver, TIME_TO_WAIT, 1)
                    wait.until_not(EC.url_changes(item["Link"]))

                    if "is QUEUED" in driver.page_source:
                        item["Status"] = "QUEUED"
                        continue
                    elif "is RUNNING" in driver.page_source:
                        item["Status"] = "RUNNING"
                        continue
                    elif "Your HPEPDOCK results" in driver.page_source:
                        item["Status"] = "FINISHED"
                    else:
                        item["Status"] = "ERROR"
                        item["Energy"] = "ERROR"
                        continue

                    # Docking Score (1st model)
                    print("Collecting data...", item["Link"])
                    element = driver.find_element(
                        By.XPATH, "/html/body/center/table[3]/tbody/tr[2]/td[1]"
                    )
                    item["Energy"] = element.text

                    # Create docking results folder
                    dock_path = f'{out_path}/docking/pep{item["Index"]}'
                    if not os.path.exists(dock_path):
                        os.makedirs(dock_path)

                    # Download and extract files containing the 10 best positions of each peptide
                    top10_models = f'{item["Link"]}top10_models.tar.gz'
                    wget.download(top10_models)
                    os.system(f"tar -xzf top10_models.tar.gz -C {dock_path}")

                    # Delete file and move models to pep folder
                    [directory] = os.listdir(dock_path)
                    topmodels = os.listdir(f"{dock_path}/{directory}")
                    for model in topmodels:
                        os.rename(
                            f"{dock_path}/{directory}/{model}", f"{dock_path}/{model}"
                        )
                    os.rmdir(f"{dock_path}/{directory}")
                    os.remove("top10_models.tar.gz")

                    print(
                        f'\nPep{item["Index"]} docking has completed. See top 10 models for it in:\n  {dock_path}\n'
                    )

                except:
                    item["Status"] = "ERROR"
                    item["Energy"] = "ERROR"
                    continue

            driver.close()

            # save energy info into csv file
            df["Energies"] = [item["Energy"] for item in items_copy]
            df.to_csv(f"{out_path}/results_dock.csv", index=False)

            # check if exists docks left
            items = [item for item in items if item["Energy"] == "NaN"]
            if len(items) > 0:
                print(f"Waiting docking... pep docks left: {len(items)}")
                print(
                    "  docks in queue:",
                    len([k for k in items_copy if k["Status"] == "QUEUED"]),
                )
                print(
                    "  docks running:",
                    len([k for k in items_copy if k["Status"] == "RUNNING"]),
                )
                print(
                    "  docks completed:",
                    len([k for k in items_copy if k["Status"] == "FINISHED"]),
                )
                print(
                    "  docks failed:",
                    len([k for k in items_copy if k["Status"] == "ERROR"]),
                )
                print(flush=True)
                time.sleep(RELOAD_TIME)
