from google.cloud import datacatalog_v1
from util.utility import init_logger

task = "datacatalog"
logger = init_logger(task)

dc_client = datacatalog_v1.DataCatalogClient()

info_types = [
    "FIRST_NAME", "LAST_NAME", "EMAIL_ADDRESS", "ADVERTISING_ID", "AGE", "CREDIT_CARD_NUMBER",
    "CREDIT_CARD_TRACK_NUMBER", "DATE", "DATE_OF_BIRTH", "DOMAIN_NAME", "ETHNIC_GROUP", "FEMALE_NAME", "GENDER",
    "GENERIC_ID", "IP_ADDRESS", "LOCATION", "LOCATION_COORDINATES", "MAC_ADDRESS", "MAC_ADDRESS_LOCAL",
    "MALE_NAME", "MEDICAL_RECORD_NUMBER", "MEDICAL_TERM", "ORGANIZATION_NAME", "PASSPORT", "PHONE_NUMBER",
    "STREET_ADDRESS", "URL", "VEHICLE_IDENTIFICATION_NUMBER"
]


def get_info_types():
    return info_types


def create_template(project_id, template_name, config, location='US'):

    tag_template = datacatalog_v1.types.TagTemplate()
    tag_template_id = template_name

    tag_template.display_name = tag_template_id

    liklihoods = ["LIKELY", "VERY_LIKELY", "POSSIBLE"]
    for field in config:

        for liklihood in liklihoods:
            id = f"{field['name']}_{liklihood}"
            desc = f"{field['name']} - {liklihood}"

            tag_template.fields[id] = datacatalog_v1.types.TagTemplateField()
            tag_template.fields[id].display_name = desc

            field_type = datacatalog_v1.types.FieldType.PrimitiveType.DOUBLE

            tag_template.fields[id].type_.primitive_type = field_type

    expected_template_name = datacatalog_v1.DataCatalogClient.tag_template_path(
        project_id, location, tag_template_id
    )

    # Create the Tag Template.

    new_tag_template = dc_client.create_tag_template(
        parent=f"projects/{project_id}/locations/{location}",
        tag_template_id=tag_template_id,
        tag_template=tag_template,
    )
    logger.log_text(f"Created template: {tag_template.name}")

    return new_tag_template


def get_tag_template(project_id, template_name, config, location="US"):

    tag_template_id = template_name

    full_template_name = f"projects/{project_id}/locations/{location}/tagTemplates/{tag_template_id}"
    request = datacatalog_v1.GetTagTemplateRequest(name=full_template_name)

    try:
        template = dc_client.get_tag_template(request=request)

    except Exception as e:
        template = create_template(project_id, template_name, config)

    return template


def get_entry(project_id, dataset, table_id):

    entry_name = f"//bigquery.googleapis.com/projects/{project_id}/datasets/{dataset}/tables/{table_id}"

    return dc_client.lookup_entry(
        request={"linked_resource": entry_name}
    )


def apply_column_tags(entry, tag_template, summary):

    for col, info in summary.items():
        tag = datacatalog_v1.types.Tag()
        tag.template = tag_template.name

        for inf, cnt in info.items():

            tag.fields[inf] = datacatalog_v1.types.TagField()
            tag.fields[inf].double_value = cnt

        tag.column = col
        dc_client.create_tag(parent=entry.name, tag=tag)


def get_findings(response):

    summary = {}
    if response.result.findings:
        for finding in response.result.findings:
            col = finding.location.content_locations[0].record_location.field_id.name
            info_type = finding.info_type.name
            if col in summary:
                if info_type in summary[col]:
                    summary[col][info_type] += 1
                else:
                    summary[col] = {
                        info_type: 1
                    }
            else:
                summary[col] = {
                    info_type: 1
                }

    return summary


def parse_bq_summary(rows):

    summary = {}
    for row in rows:
        col = row['field_name']
        info_type = row['name']
        likelihood = row['likelihood']
        val = row['count_total']

        id = f"{info_type}_{likelihood}"

        if col in summary:
            summary[col][id] = val

        else:
            summary[col] = {
                id: val
            }

    return summary
