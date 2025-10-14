# upload_files.py

import os
import csv
import requests
from typing import Dict, Union


class UploadFiles:
    def __init__(self, upload_url: str, auth_token: str):
        self.upload_url = upload_url
        self.headers = {"Authorization": auth_token}

    def upload(self, filepath: str) -> Dict[str, Union[int, str, None]]:
        filename = os.path.basename(filepath)
        with open(filepath, "rb") as f:
            files = {
                "file": (
                    filename,
                    f,
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            }
            resp = requests.post(
                self.upload_url,
                headers=self.headers,
                files=files
            )

        # parse JSON if possible
        file_id = None
        try:
            payload = resp.json()
            file_id = payload.get("file_id")
        except ValueError:
            # response wasn’t JSON
            pass

        return {
            "status_code": resp.status_code,
            "response_text": resp.text,
            "file_id": file_id
        }

    def upload_directory(
        self,
        directory: str,
        csv_path: str = "uploaded_files_with_id.csv"
    ) -> Dict[str, Dict[str, Union[int, str, None]]]:
        results: Dict[str, Dict[str, Union[int, str, None]]] = {}
        rows = []

        for name in os.listdir(directory):
            path = os.path.join(directory, name)
            if not os.path.isfile(path):
                continue

            result = self.upload(path)
            code = result["status_code"]
            if code >= 400:
                print(f"✖ Failed {name}: {code}\n  → {result['response_text']}")
            else:
                print(f"✔ Uploaded {name}: {code}")
                # only record successful uploads
                rows.append({
                    "display_name": name,
                    "file_id": result["file_id"]
                })

            results[name] = result

        # write CSV of successful uploads
        with open(csv_path, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=["display_name", "file_id"])
            writer.writeheader()
            writer.writerows(rows)

        print(f"\nSaved {len(rows)} entries to {csv_path}")
        return results
