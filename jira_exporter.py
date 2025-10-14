import os
import re
import glob
import csv
import requests
import pandas as pd
from typing import Dict, List, Any, Optional

class JiraExporter:
    """
    Fetches issues from Jira using one or two JQL queries,
    cleans out old CSV/XLSX files, writes per-CIS Excel files for the primary JQL,
    and writes a single Datsm_issues.xlsx for the secondary JQL.
    """

    def __init__(
        self,
        jira_url: str,
        username: str,
        password: str,
        jql: str,
        output_dir: str,
        cis_csv_path: Optional[str] = None,
        second_jql: Optional[str] = None,
        max_results: int = 100
    ):
        self.jira_url      = jira_url.rstrip("/")
        self.username      = username
        self.password      = password
        self.jql           = jql
        self.second_jql    = second_jql
        self.output_dir    = output_dir
        self.cis_csv_path  = cis_csv_path
        self.max_results   = max_results

        os.makedirs(self.output_dir, exist_ok=True)

        # Load CIS → filename mapping (if provided)
        self.cis_mapping: Dict[str, str] = {}
        if self.cis_csv_path:
            self.cis_mapping = self._load_cis_mapping()

        # Prepare a requests.Session for reuse
        self.session = requests.Session()
        self.session.auth = (self.username, self.password)

    def _load_cis_mapping(self) -> Dict[str, str]:
        mapping: Dict[str, str] = {}
        with open(self.cis_csv_path, newline="", encoding="utf-8-sig") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                key = row.get("displayName", "").strip()
                val = row.get("filename", "").strip()
                if key and val:
                    mapping[key] = val
        return mapping

    def _sanitize_filename(self, name: str) -> str:
        safe = re.sub(r"[^\w\-_ ]+", "_", name)
        return safe[:50].strip()

    def _extract_cis(self, raw: Any) -> str:
        if isinstance(raw, list):
            vals: List[str] = []
            for e in raw:
                if isinstance(e, dict):
                    vals.append(e.get("displayName") or
                                e.get("value") or
                                e.get("name", ""))
                else:
                    vals.append(str(e))
            return ", ".join(vals) or "Unknown"

        if isinstance(raw, dict):
            return (raw.get("displayName") or
                    raw.get("value") or
                    raw.get("name") or
                    "Unknown")

        return str(raw) if raw else "Unknown"

    def _get_safe_name(self, cis_val: str) -> str:
        cis_norm = cis_val.strip()
        for src, target in self.cis_mapping.items():
            if src in cis_norm:
                return target

        base = re.sub(r"_+NTC-[^_]+_*$", "", cis_norm).strip()
        return self._sanitize_filename(base.replace(" ", "_"))

    def _fetch_page(self, jql: str, start_at: int) -> Dict[str, Any]:
        url = f"{self.jira_url}/rest/api/2/search"
        params = {
            "jql":        jql,
            "startAt":    start_at,
            "maxResults": self.max_results,
            "fields":     ",".join([
                "key", "summary", "assignee", "status", "priority",
                "customfield_18502",  # Owner
                "customfield_17902"   # NTA TPS CIs
            ])
        }
        resp = self.session.get(url, params=params)
        if resp.status_code >= 400:
            print(f"\n❗️ Jira returned HTTP {resp.status_code}")
            print("→ URL:", resp.url)
            print("→ Body:", resp.text, "\n")
            resp.raise_for_status()
        return resp.json()

    def export(self) -> None:
        # 1) Delete any existing .csv or .xlsx in the output folder
        patterns = ["*.csv", "*.xlsx"]
        for pat in patterns:
            for path in glob.glob(os.path.join(self.output_dir, pat)):
                try:
                    os.remove(path)
                    print(f"Deleted old file: {path}")
                except Exception as e:
                    print(f"Error deleting {path}: {e}")

        # 2) Primary JQL → per-CIS Excel files
        primary_rows: List[Dict[str, Any]] = []
        start_at = 0
        while True:
            data = self._fetch_page(self.jql, start_at)
            issues = data.get("issues", [])
            if not issues:
                break

            for issue in issues:
                f = issue["fields"]
                primary_rows.append({
                    "Key":         issue["key"],
                    "Owner":       self._extract_cis(f.get("customfield_18502")),
                    "Summary":     f.get("summary", ""),
                    "Assignee":    (f.get("assignee") or {}).get("displayName", "Unassigned"),
                    "Status":      (f.get("status")   or {}).get("name", ""),
                    "Priority":    (f.get("priority") or {}).get("name", ""),
                    "NTA TPS CIs": self._extract_cis(f.get("customfield_17902"))
                })
            start_at += len(issues)

        df_primary = pd.DataFrame(primary_rows)
        for cis_val, group_df in df_primary.groupby("NTA TPS CIs"):
            safe_name = self._get_safe_name(cis_val)
            out_path = os.path.join(self.output_dir, f"{safe_name}.xlsx")
            group_df.to_excel(out_path, index=False)
            print(f"Saved {len(group_df)} tickets to {out_path}")

        # 3) Secondary JQL → single Datsm_issues.xlsx
        if self.second_jql:
            datsm_rows: List[Dict[str, Any]] = []
            start_at = 0
            while True:
                data2 = self._fetch_page(self.second_jql, start_at)
                issues2 = data2.get("issues", [])
                if not issues2:
                    break

                for issue in issues2:
                    f = issue["fields"]
                    datsm_rows.append({
                        "Key":      issue["key"],
                        "Owner":    self._extract_cis(f.get("customfield_18502")),
                        "Summary":  f.get("summary", ""),
                        "Assignee": (f.get("assignee") or {}).get("displayName", "Unassigned"),
                        "Status":   (f.get("status")   or {}).get("name", ""),
                        "Priority": (f.get("priority") or {}).get("name", "")
                    })
                start_at += len(issues2)

            df_datsm = pd.DataFrame(datsm_rows)
            path_datsm = os.path.join(self.output_dir, "Datsm_issues.xlsx")
            df_datsm.to_excel(path_datsm, index=False)
            print(f"Saved {len(df_datsm)} Datsm tickets to {path_datsm}")
