# run_export.py

from jira_exporter import JiraExporter
from upload_files import UploadFiles
from send_files import FileSender

if __name__ == "__main__":
    # (1) Export step as before
    JIRA_URL   = "https://jira.mohaymen.ir"
    USERNAME   = "t.rashki"
    PASSWORD   = "*****"
    # First JQL (NTA project)
    JQL        = (
        'project = "NTA TPS SM"  AND issuetype = Incident '
        'AND filter = \'32233\' AND status in (New, "In Progress - 2", '
        '"In Progress - 1") AND cf[18502] = SRE  '
        'AND "Time to resolution" < remaining("1h")'
    )
    # Secondary JQL (Datsm project)
    SECOND_JQL = """project = "DAT SM" AND status not in (Closed, Resolved, Canceled) AND issueFunction in linkedIssuesOf(
        "project = 'NTA TPS SM' AND status = 'In Progress - 3' AND issuetype = Incident",
        "relates to"
    )"""
    OUTPUT_DIR = "nta_tps_outputs"
    CIS_CSV    = "/data/SLA_Passed/metadata/cis_name_mapping.csv"

    exporter = JiraExporter(
        jira_url=JIRA_URL,
        username=USERNAME,
        password=PASSWORD,
        jql=JQL,
        output_dir=OUTPUT_DIR,
        cis_csv_path=CIS_CSV,
        second_jql   = SECOND_JQL
    )
    exporter.export()

    # (2) Upload step + CSV recording
    UPLOAD_URL = "https://bui.splus.ir/v1/file/upload"
    AUTH_TOKEN = "eyJhbGciOiJIUzUxMiJ9.eyJzYWx0IjoiNjVlNWYyMDctNTA4YS00Yjc1LWFkMzgtNWE2N2VmZTVhYmVlIiwiaWQiOiI3NDIifQ.fbMdAy6tOv9pCG_s6comuykE98orrLIAi-lNVkKHjTY_nrVtYoHs5v529d8TSYpOJ_Fr2iHjj01n3vy3xEQDAg"

    uploader = UploadFiles(upload_url=UPLOAD_URL, auth_token=AUTH_TOKEN)
    summary = uploader.upload_directory(
        directory=OUTPUT_DIR,
        csv_path="/data/SLA_Passed/metadata/uploaded_files_with_id.csv"
    )

    # existing summary printout, now with file_id available
    print("\nUpload summary:")
    for fname, info in summary.items():
        status = info["status_code"]
        fid = info.get("file_id")
        print(f"  {fname}: status={status}, file_id={fid}")
    
    # (3) Send messages and log to file
    SEND_URL       = "https://bui.splus.ir/v1/messages/send"
    AUTH_TOKEN_MSG = "eyJhbGciOiJIUzUxMiJ9.eyJzYWx0IjoiNjVlNWYyMDctNTA4YS00Yjc1LWFkMzgtNWE2N2VmZTVhYmVlIiwiaWQiOiI3NDIifQ.fbMdAy6tOv9pCG_s6comuykE98orrLIAi-lNVkKHjTY_nrVtYoHs5v529d8TSYpOJ_Fr2iHjj01n3vy3xEQDAg"
    FILE_ID_CSV    = "/data/SLA_Passed/metadata/uploaded_files_with_id.csv"
    RECIPIENTS_CSV = "/data/SLA_Passed/metadata/files_numbers_text.csv"
    LOG_DIRECTORY  = "message_logs"  # where logs will live

    sender = FileSender(
        send_url       = SEND_URL,
        auth_token     = AUTH_TOKEN_MSG,
        file_id_csv    = FILE_ID_CSV,
        recipients_csv = RECIPIENTS_CSV,
        log_dir        = LOG_DIRECTORY
    )

    sender.send_all()

    print(f"\nAll send attempts have been logged in '{LOG_DIRECTORY}'")
