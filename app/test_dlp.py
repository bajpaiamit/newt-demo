import time

from google.cloud import dlp_v2

dlp_client = dlp_v2.DlpServiceClient()

_info_types = [
            "FIRST_NAME", "LAST_NAME", "EMAIL_ADDRESS", "ADVERTISING_ID", "AGE", "CREDIT_CARD_NUMBER",
            "CREDIT_CARD_TRACK_NUMBER", "DATE", "DATE_OF_BIRTH", "DOMAIN_NAME", "ETHNIC_GROUP", "FEMALE_NAME", "GENDER",
            "GENERIC_ID", "IP_ADDRESS", "LOCATION", "LOCATION_COORDINATES", "MAC_ADDRESS", "MAC_ADDRESS_LOCAL",
            "MALE_NAME", "MEDICAL_RECORD_NUMBER", "MEDICAL_TERM", "ORGANIZATION_NAME", "PASSPORT", "PHONE_NUMBER",
            "STREET_ADDRESS", "URL", "VEHICLE_IDENTIFICATION_NUMBER"]

info_types = [
    {"name": info_type} for info_type in _info_types
]




parent = f"projects/sbox-jason-blythe/locations/global"


inspect_config = {
    "info_types": info_types,
    "min_likelihood": "POSSIBLE",
}

storage_config = {
    "big_query_options": {
        "table_reference": {
            "project_id": "sbox-jason-blythe",
            "table_id": "CUSTOMER",
            "dataset_id": "tpch"
        },
        "identifying_fields": [],
        "excluded_fields": [],
        "included_fields": [],
        "rows_limit": 2000
    }
}

actions = {
    "save_findings": {
        "output_config": {
            "table": {
                "project_id": "sbox-jason-blythe",
                "dataset_id": "tpch"
            }
        }
    }
}

inspect_job = {
    "inspect_config": inspect_config,
    "storage_config": storage_config,
    "actions": [actions]
}

response = dlp_client.create_dlp_job(request={"parent": parent, "inspect_job": inspect_job})

request = dlp_v2.GetDlpJobRequest(
    name=response.name,
)

job = dlp_client.get_dlp_job(request=request)

while job.state.name not in ['DONE', 'CANCELED', 'FAILED']:
    print(job.inspect_details.requested_options.job_config.actions[0].save_findings.output_config.table.table_id)
    time.sleep(5)
    job = dlp_client.get_dlp_job(request=request)


res = job.inspect_details.result.info_type_stats

for r in res:
    print(r)

