import os
import csv
import json
import re
import glob
import requests
import datetime
from typing import Dict, List

MAX_LOG_SIZE = 2 * 1024 * 1024  # 2 MB

class FileSender:
    """
    Sends messages with file attachments to recipients.
    Logs each attempt in a JSON array, rotating logs only when size exceeds 2MB.
    """

    def __init__(
        self,
        send_url: str,
        auth_token: str,
        file_id_csv: str,
        recipients_csv: str,
        log_dir: str
    ):
        self.send_url       = send_url
        self.headers        = {
            "Authorization": auth_token,
            "Content-Type":  "application/json"
        }
        self.file_id_csv    = file_id_csv
        self.recipients_csv = recipients_csv
        self.log_dir        = log_dir

        os.makedirs(self.log_dir, exist_ok=True)
        self.file_mapping = self._load_file_ids()
        self.recipients   = self._load_recipients()
        self.log_index    = self._find_latest_log_index()

    def _find_latest_log_index(self) -> int:
        files = glob.glob(os.path.join(self.log_dir, "messages_*.json"))
        idxs = []
        for f in files:
            m = re.match(r".*messages_(\d+)\.json$", f)
            if m:
                idxs.append(int(m.group(1)))
        return max(idxs) if idxs else 0

    def _get_log_path(self) -> str:
        return os.path.join(self.log_dir, f"messages_{self.log_index}.json")

    def _rotate_if_needed(self) -> None:
        path = self._get_log_path()
        if os.path.exists(path) and os.path.getsize(path) >= MAX_LOG_SIZE:
            self.log_index += 1

    def _write_log(self, entry: Dict) -> None:
        """
        Append `entry` into the current JSON array log file,
        rotating to a new file if size >= MAX_LOG_SIZE.
        """
        try:
            self._rotate_if_needed()
            path = self._get_log_path()
            data = json.dumps(entry, ensure_ascii=False)

            # If file doesn't exist or is empty, start a new JSON array
            if not os.path.exists(path) or os.path.getsize(path) == 0:
                with open(path, "w", encoding="utf-8") as f:
                    f.write("[" + data + "]")
                return

            # Otherwise, append into the existing array:
            # 1) open in read+write
            # 2) seek back one char (the closing bracket)
            # 3) truncate
            # 4) write comma + new entry + closing bracket
            with open(path, "r+", encoding="utf-8") as f:
                f.seek(0, os.SEEK_END)
                # step back over the final ']'
                f.seek(f.tell() - 1)
                f.truncate()
                f.write(",\n" + data + "]")

        except Exception as e:
            print("ERROR writing log:", e)

    def _load_file_ids(self) -> Dict[str, str]:
        mapping: Dict[str, str] = {}
        with open(self.file_id_csv, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                name    = row.get("display_name", "").strip()
                file_id = row.get("file_id", "").strip()
                if name and file_id:
                    mapping[name] = file_id
        return mapping

    def _load_recipients(self) -> List[Dict[str, str]]:
        recs: List[Dict[str, str]] = []
        with open(self.recipients_csv, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                name  = row.get("\ufeffdisplay_name", "").strip()
                raw   = row.get("Phone_number", "")
                phone = raw.replace("phone_number :", "").strip()
                text  = row.get("text", "").strip()
                if name and phone:
                    recs.append({
                        "display_name": name,
                        "phone_number": phone,
                        "text": text
                    })
        return recs

    def send_message(self, phone_number: str, text: str, file_id: str):
        payload = {
            "phone_number": phone_number,
            "text":         text,
            "file_id":      file_id
        }
        resp = requests.post(self.send_url, headers=self.headers, json=payload)
        resp.raise_for_status()
        return resp

    def send_all(self) -> None:
        print("📤 Starting message dispatch…")
        for rec in self.recipients:
            name    = rec["display_name"]
            phone   = rec["phone_number"]
            text    = rec["text"]
            file_id = self.file_mapping.get(name)

            now = datetime.datetime.now().isoformat()
            entry = {
                "timestamp":    now,
                "display_name": name,
                "phone_number": phone,
                "file_id":      file_id,
                "status":       None,
                "error":        None
            }

            if not file_id:
                entry["status"] = "SKIPPED"
                print(f"⚠️ Skipped {name} — no file_id")
                self._write_log(entry)
                continue

            try:
                resp = self.send_message(phone, text, file_id)
                entry["status"] = resp.status_code
                print(f"✔️ Sent to {name}: {resp.status_code}")
            except Exception as e:
                entry["error"] = str(e)
                print(f"❌ Error sending to {name}: {e}")
            finally:
                self._write_log(entry)

        print(f"📁 All send attempts logged in '{self.log_dir}'")
