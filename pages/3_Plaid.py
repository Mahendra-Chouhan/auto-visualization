import streamlit as st
import logging
from lida import Manager, TextGenerationConfig, llm
import uuid
import pprint
import pandas as pd
from urllib.error import URLError
from datetime import datetime
import src.st_utils as st_utils
import src.utils as utils
import src.preprocess_plaid as preprocess_plaid
import src.plaid as plaid
import src.visuals as visualization
import src.reporting_cidds as reporting_cidds


st.set_page_config(page_title="Plaid",  layout="wide", page_icon="📈")

text_gen = llm(provider="openai")
textgen_config = TextGenerationConfig(
    n=1, temperature=0.5, model="gpt-3.5-turbo-0301", use_cache=True
)
lida = Manager(text_gen=text_gen)

@st.cache_data(ttl=3600)
def load_tokens():
    # Perform expensive computation here or
    # fetch data from the web here
    plaid.get_access_token()

load_tokens()


user_id = 2
tenant_name = utils.get_tenant_names()
logger = logging.getLogger()
st.header("Plaid")
st.subheader("Help people manage, budget, and make sense of their money")
# st.write("CIDDS (Coburg Intrusion Detection Data Sets) is a concept to create evaluation data sets for anomaly-based network intrusion detection systems. Since the IT industry is constantly evolving, attackers are forced to adapt and find new ways to penetrate their target of interest")
application = "Plaid"
custom_kpis = pd.read_csv('data/KPIs/base_kpis.csv')  
custom_kpis = custom_kpis[custom_kpis['application'] == application] 
pp = pprint.PrettyPrinter(indent=2)
template_names = utils.get_templates(user_id, application)
accounts_list = plaid.get_accounts()

# Initialize visualizations in session state
if f"{application}_df" not in st.session_state:
    st_utils.init_session()
else:
    st_utils.Preload(lida, textgen_config, application)

with st.sidebar.form(key="form"):
    st.write(" ## Get Data")
    selected_accounts = st.multiselect('Select Accounts', [account["name"] for account in accounts_list], key="accounts")
    start_date = st.date_input("Start Date", key="start_date")
    end_date = st.date_input("End Date", key="end_date", max_value=datetime.today())
    submit_button = st.form_submit_button(label="Submit", on_click=st_utils.init_session)
    

if submit_button:
    response = plaid.get_transactions(selected_accounts, start_date, end_date, accounts_list)
    df = preprocess_plaid.main(response, accounts_list)
    
    # st.write(stock_info.info["longBusinessSummary"])
    with st.container(border=True):
            st.dataframe(df.head(7), hide_index=True, use_container_width=True)  # Display the dataframe
    st.session_state[f"{application}_df"] = df

    textual_summary = visualization.generate_textual_summary(lida, textgen_config, df)
    
    my_complex_dict = pprint.pformat(textual_summary)
    logger.info(f"Summary: \n{my_complex_dict}")
    # Generate summary using LIDA
    st.session_state[f"{application}_summary"] = textual_summary
    st.header("Visualizations")
    goals = lida.goals(textual_summary, n=4)
    st.write(goals)
    # # Process KPI queries
    for index, row in custom_kpis.iterrows():
        st_utils.visuals(lida, textgen_config, row['KPI_text'], row['graph_title'], 
                            textual_summary, application)
if f"{application}_df" in st.session_state:
    worksoft_df = st.session_state[f"{application}_df"] 
    textual_summary = visualization.generate_textual_summary(lida, textgen_config, worksoft_df) 
    with st.container(border=True):
        st.write("##### Additional Visualizations")
        id = str(uuid.uuid4())
        for kpi, col in zip(st.session_state[f"{application}_KPIs"][:4], st.columns(4)):
            col.button(kpi["text"], key=str(uuid.uuid4()),
                    on_click=st_utils.visual_edit, args=(lida, textgen_config, id, textual_summary, application, kpi["KPI"], kpi["text"], ), disabled=kpi["disabled"])

    with st.container(border=True):
        st.write(" ##### Custom Visualizations")
        id = str(uuid.uuid4())
        kpi_query = st.text_input("",
                                 on_change=st_utils.visual_edit, args=(lida, textgen_config, id, textual_summary, application), key=id ,placeholder="Enter your custom prompt")
if len(st.session_state[f"{application}_visualizations"]):
    if len(template_names):
        with st.sidebar:
            with st.container(border=True):
                st.write(" ## Saved Templates")
                for template in template_names:
                    st.button(template["name"], on_click=st_utils.load_template, args=(template["path"], ))

    with st.sidebar.form(key="save_template"):
        template_name = st.text_input("Template name", key="template_name", placeholder="Weekly-template")
        save_template = st.form_submit_button(label="Save Template")

    if st.sidebar.button('Generate Report', type="primary"):
        with st.container(border=True):
            tenant_name = "CIDDS"
            start_date = st.session_state.start_date
            end_date = st.session_state.end_date
            
            visualization_details = st.session_state[f"{application}_visualizations"]
            if len(visualization_details):
                # print(tenant_name, selected_applications, start_date, end_date, kpi_texts,
                #                           visualization_paths)
                pdf_path = reporting_cidds.generate_report(tenant_name, application, start_date, end_date, visualization_details)
                st_utils.displayPDF(pdf_path)
            else:
                st.write("Please create some KPIs before generating report")

    if save_template:        
        st_utils.save_template(user_id, application, template_name)