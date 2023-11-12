from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

import pandas as pd
import time
import wget
import os


class Scraping:
    def __init__(self, task_id):
        self.task_id = task_id
        self.options = Options()
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--headless")

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

        # Time to reload page in seconds
        reloadtime = 120

        print("\nStarting docking scraping...")
        print(
            f"It's will try to do the docking scraping every {reloadtime} seconds.\n",
            flush=True,
        )

        while len(items) > 0:
            driver = Chrome(options=self.options)
            for item in items:
                driver.get(item["Link"])
                time.sleep(3)

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
                time.sleep(reloadtime)
