import json
import os
import base64
import pandas as pd


def get_tenant_names():
    tenant_names = []
    #################################### Mapping Tenant name with ID ############
    with open("data/mapping.json", "r") as outfile:
        data = json.load(outfile)
        for entry in data:
            tenant_names.append(entry["Name"])
    # print("the tenant names are", tenant_name)
    return tenant_names

def get_status_message(status_code, platform):
    message = "Something went wrong"
    if status_code == 504 and platform == "deereai":
        message = "DeereAi API Gateway timeout. "

    return message

def get_kpis(application):
    kpi_list = []
    if application == "CIDDS":
        
        kpi_dict = dict()
        kpi_dict["text"] = "Network Traffic Volume"
        kpi_dict["KPI"] = "Generate a line chart with the x-axis representing time (Day or Month) and the y-axis representing the total bytes or packets" 
        kpi_dict["disabled"] = False
        kpi_list.append(kpi_dict)

        kpi_dict = dict()
        kpi_dict["text"] = "Daily Protocol Distribution"
        kpi_dict["KPI"] = "Generate a bar graph to show day trend of protocol" 
        kpi_dict["disabled"] = False
        kpi_list.append(kpi_dict)

        kpi_dict = dict()
        kpi_dict["text"] = "Network Traffic by IP Address"
        kpi_dict["KPI"] = "Create an interactive horizontal bar chart or treemap to display the top source or destination IP addresses contributing to the network traffic" 
        kpi_dict["disabled"] = False
        kpi_list.append(kpi_dict)

        kpi_dict = dict()
        kpi_dict["text"] = "Traffic Composition by Class"
        kpi_dict["KPI"] = "Create an interactive stacked bar chart to visualize the distribution of network traffic across different classes (e.g., normal, suspicious, unknown)" 
        kpi_dict["disabled"] = False
        kpi_list.append(kpi_dict)


    return kpi_list

def mapping_tenant_name(tenant_name_selection):
    with open("data/mapping.json", "r") as outfile:
        data = json.load(outfile)
        for entry in data:
            if entry["Name"] == tenant_name_selection:
                tenant_Id = entry["TenantId"]
    return tenant_Id

def get_car_df():
    df = pd.read_csv("data/cars.csv")
    print(f"NUmber of records {len(df)}")
    return df

def get_df_basics(df):
    SuiteNames = list(df.SuiteName.unique())
    basic_details = (
        f"Total number of records:{len(df)}, Unique Suits id {len(SuiteNames)}"
    )
    return basic_details

def get_templates(user_id, application_name):
    # get all template of user.
    template_list = []
    path = f"data/KPIs/{application_name}"
    obj = os.scandir(path)
    print(obj)
    for entry in obj:
        if entry.is_file():
            if str(user_id) == str(entry.name.split("_")[0]) and entry.name.split("_")[1]==application_name:
                temp = dict()
                temp["name"] = entry.name.split("_")[-1].split(".json")[0] 
                temp["application"] = application_name
                temp["path"] = entry.path
                template_list.append(temp)
    return template_list 


def pdf_to_base_64(file):
    #function to display the PDF of a given file 

    # Opening file from file path. this is used to open the file from a website rather than local
    with open(file, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        return base64_pdf
