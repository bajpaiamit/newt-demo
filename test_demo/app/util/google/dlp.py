from google.cloud import dlp_v2

dlp_client = dlp_v2.DlpServiceClient()


def inspect_content(parent, inspect_config, inspect_item):
    return dlp_client.inspect_content(
        request={"parent": parent, "inspect_config": inspect_config, "item": inspect_item}
    )


def get_dlp_job_request(job_name):

    request = dlp_v2.GetDlpJobRequest(
        name=job_name,
    )

    return request


def get_dlp_job(request):

    job = dlp_client.get_dlp_job(request=request)

    return job


def create_dlp_job(parent, inspect_job):

    response = dlp_client.create_dlp_job(request={"parent": parent, "inspect_job": inspect_job})
    return response


def get_inspect_config(info_types, min_likelihood):

    return {
        "info_types": info_types,
        "min_likelihood": min_likelihood,
    }


def get_big_query_storage_options(project_id, dataset, table_id, identifying_fields=[], excluded_fields=[],
                                  included_fields=[], rows_limit=2000):

    return {
        "table_reference": {
            "project_id": project_id,
            "table_id": table_id,
            "dataset_id": dataset
        },
        "identifying_fields": identifying_fields,
        "excluded_fields": excluded_fields,
        "included_fields": included_fields,
        "rows_limit": rows_limit
    }


def get_storage_config(data_store_options=None, cloud_storage_options=None, big_query_options=None, hybrid_options=None):
    if data_store_options is None and cloud_storage_options is None and big_query_options is None \
            and hybrid_options is None:
        raise "At least one set of Options needs to be set"

    storage_config = {}

    if big_query_options is not None:
        storage_config['big_query_options'] = big_query_options

    if data_store_options is not None:
        """
        IMPLEMENT LATER
        """
        pass

    if cloud_storage_options is not None:
        """
        IMPLEMENT LATER
        """
        pass

    if hybrid_options is not None:
        """
        IMPLEMENT LATER
        """
        pass

    return storage_config


def create_save_finding_action(project_id, dataset, table_id=None):

    table_config = {
        "project_id": project_id,
        "dataset_id": dataset
    }

    if table_id is not None:
        table_config['table_id'] = table_id

    table_config = {
        "output_config": {
            "table": table_config
        }
    }

    return {
        "save_findings": table_config
    }
