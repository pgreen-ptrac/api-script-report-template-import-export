from operator import itemgetter
import os

from input_utils import *
from auth_utils import *
from request_utils import *


script_info = ["===================================================================",
               "= Report Template Import/Export Script                            =",
               "=-----------------------------------------------------------------=",
               "=  Used to export a report template and save it as a JSON file.   =",
               "=  You can then keep the file as a backup or import it to a       =",
               "=  different instance of Plextrac.                                =",
               "=                                                                 =",
               "=  Future link to documentation                                   =",
               "=  Future link to Plextrac Labs example scripts                   =",
               "==================================================================="
            ]


# import handler
def handle_import(auth):
    json_file_path = handle_input_path()

    try:
        with open(json_file_path, 'r', encoding="utf8") as file:
            json_data = json.load(file)
    except Exception as e:
        if prompt_retry(f'Error loading file: {e}'):
            return handle_import(auth)

    if (
        json_data.get('template_name', None) == None or
        json_data.get('export_template', None) == None
    ):
        if prompt_retry('Err: Json file is not a valid Report Template'):
            return handle_import(auth)

    response = request_import_report_template(base_url, auth.auth_headers, auth.tenant_id, json_data)
    if response.status == "success":
        print(f'Success! Report Template imported')
        print(f'You now have the "{json_data["template_name"]}" option in the Report Template dropdown field on the Report Details tab')
        print(f'View or edit the new report template in the Template section of the Account Admin page')
    else:
        if prompt_retry("Import failed."):
            return handle_import(auth)
   

# export handler
def handle_export(base_url, auth_headers, tenant_id):
    report_templates = request_list_report_templates(base_url, auth.auth_headers, tenant_id)

    print(f'List of Report Templates in tenant {tenant_id}:')
    for index, report_template in enumerate(report_templates):
        print(f'Index: {index}   Name: {report_template.get("data").get("template_name")}')

    report_template_index = prompt_user_list("Please enter the report template ID from the list above that you want to export.", "Index out of range.", len(report_templates))
    report_template_id = report_templates[report_template_index]["data"]["doc_id"]
    print(f'Selected Report Template: {report_template_index} - {report_templates[report_template_index]["data"]["template_name"]}')

    print('\nRetrieving Report Template Data')
    response = request_get_report_template(base_url, auth.auth_headers, tenant_id, report_template_id)
    data = {
        "template_name": response.get('template_name'),
        "export_template": "default",
        "custom_fields": response.get('custom_fields', []),
        "report_custom_fields": response.get('report_custom_fields', [])
    }

    print('Exporting Report Template data')
    export_file_dir = "exports"
    if os.path.isdir(export_file_dir) != True:
        print(f'Creating \'{export_file_dir}\' folder')
        os.mkdir('exports')
    
    export_file_name = f'Report_Template_{data["template_name"].replace(" ", "_").replace("/","-")}.json'
    export_file_path = export_file_dir + '/' + export_file_name
    try:
        with open(export_file_path, 'w', encoding="utf8") as file:
            json.dump(data, file)
    except Exception as e:
        print(f'Error creating file: {e}')
        return

    print(f'Report Template exported successfully!')


if __name__ == '__main__':
    for i in script_info:
        print(i)
    
    base_url, cf_token = itemgetter('base_url', 'cf_token')(handle_instance_url())

    auth = Auth(base_url)
    if cf_token != None:
        auth.add_cf_auth_header(cf_token)
    auth.handle_auth()
    
    operation = prompt_user_options("Do you want to import or export a Plextrac Report Template", "Invalid option.", ['import', 'export'])

    if operation == 'import':
        print('\n---Loading Imports---')
        handle_import(auth)
    if operation == 'export':
        print('\n---Loading Exports---')
        handle_export(auth)
