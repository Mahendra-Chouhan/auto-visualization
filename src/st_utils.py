import logging
import uuid
import json
import copy
import pprint
import time
import httpx
import json
import src.utils as utils
import streamlit as st
from datetime import datetime
import src.visuals as visualization

from lida.datamodel import Goal
logger = logging.getLogger()

is_diaplay_explability = True


def visual_edit(lida, textgen_config, id:str, textual_summary, application, kpi_query=None, graph_title=""):
    logger.debug("****inside edits st_utils  zone****")
    if kpi_query is not None:
        goal = Goal(question = graph_title, visualization=kpi_query, rationale="")
        edited_query = kpi_query
       
    else:
        edited_query = st.session_state[id]
        goal = Goal(question = graph_title, visualization=edited_query, rationale="")
    # find the id removed the record. 
    visuals_dict = dict()
    visuals_dict["id"] = str(uuid.uuid4())
    visuals_dict["kpi_query"] = edited_query
    logger.info(edited_query)
    for visual in st.session_state[f"{application}_visualizations"]:
        if visual["id"] == id:
            st.session_state[f"{application}_visualizations"].remove(visual)
    try:
        # textual_summary = visualization.generate_textual_summary(st.session_state["worksoft_df"])
        images, visuals_paths, visuals = visualization.get_visuals(lida, textgen_config, textual_summary, goal)
        
        if len(visuals) > 0:
            
            if is_diaplay_explability:
                time.sleep(2)
                visuals_description = visualization.get_explaination(lida, textgen_config, visuals[0])
                visuals_dict["visualizations_description"] = visuals_description[0]
            
            visuals_dict["Date_of_creation"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            visuals_dict["Date_of_updation"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            visuals_dict["last_executed"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            visuals_dict["is_active"] = True
            visuals_dict["code"] = visuals[0].code
            visuals_dict["visualizations"] = images[0]
            visuals_dict["visualizations_path"] = visuals_paths[0]
            st.session_state[f"{application}_visualizations"].append(visuals_dict)
        else:
            st.session_state[f"{application}_visualizations"].append(visuals_dict)
    except httpx.HTTPStatusError as exc:
            # st.write(f":cross_mark: Error in this request {kpi_query}")
            utils.get_status_message(exc.response.status_code, "deereai")
            st.warning(f"I am unable to process the request due to: {exc.response.status_code} error", icon="😔")

def displayPDF(file):
    # Opening file from file path. this is used to open the file from a website rather than local
    base64_pdf = utils.pdf_to_base_64(file)
    st.write("## Report")
    with st.container(border=True):
        pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="950" type="application/pdf"></iframe>'

        # Displaying File
        st.markdown(pdf_display, unsafe_allow_html=True)


# def load_lida():
#     logger.info("Lida loaded")
    
#     st.session_state["textgen_config"] = textgen_config 
#     st.session_state["lida"] = lida


def init_session():
    if "CIDDS_df" in st.session_state:
        del st.session_state["CIDDS_df"]
    st.session_state["CIDDS_visualizations"] = []
    st.session_state["CIDDS_KPIs"] = utils.get_kpis("CIDDS")
    

def visuals(lida, textgen_config, kpi_query, graph_title, textual_summary, application):
    with st.container(border=True):
        goal = Goal(question = graph_title, visualization=kpi_query, rationale="")
        visuals_dict = dict()
        visuals_dict["id"] = str(uuid.uuid4())
        visuals_dict["kpi_query"] = kpi_query
        st.text_input("Prompt", value=kpi_query, key=visuals_dict["id"],
                      on_change=visual_edit, args=(lida, textgen_config, visuals_dict["id"], textual_summary, application))
        try:
            # textual_summary = visualization.generate_textual_summary(st.session_state["worksoft_df"]
            # )
            images, visuals_paths, visuals = visualization.get_visuals(lida, textgen_config, textual_summary,
                                            goal)
            if len(visuals) > 0:
                st.image(images[0], use_column_width="auto")
                if is_diaplay_explability:
                    time.sleep(2)
                    visuals_description = visualization.get_explaination(lida, textgen_config, visuals[0])
                    with st.expander("See explanation"):
                        visuals_dict["visualizations_description"] = visuals_description[0]
                        for description in visuals_description[0]:
                            st.markdown(f"""**{description['section']}**""")
                            st.write(description["explanation"])
                            st.divider()
                visuals_dict["Date_of_creation"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                visuals_dict["Date_of_updation"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                visuals_dict["last_executed"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                visuals_dict["is_active"] = True
                
                visuals_dict["code"] = visuals[0].code
                visuals_dict["visualizations"] = images[0]
                visuals_dict["visualizations_path"] = visuals_paths[0]
                st.session_state[f"{application}_visualizations"].append(visuals_dict)  # Add PIL image to list
                
            else:
                st.warning(f"No visualizations generated for KPI {kpi_query}.")
        except httpx.HTTPStatusError as exc:
            # st.write(f":cross_mark: Error in this request {kpi_query}")
            utils.get_status_message(exc.response.status_code, "deereai")
            st.warning(f"I am unable to process the request due to: {exc.response.status_code} error", icon="😔")

def load_template(path):
    # load json
    with open(path, 'r') as myfile:
        template=json.load(myfile)
    st.session_state["visualizations"] = template["KPI_list"]

def Preload(lida, textgen_config, application, except_ids=[]):
    logger.info(f"Preloaded for {application}")

    if application == "CIDDS" and "cidds_df" in st.session_state:
        with st.container(border=True):
            st.dataframe(st.session_state["cidds_df"].head(7), hide_index=True)
        st.header("Visualizations")
        if f"{application}_visualizations" in st.session_state:
            my_complex_dict = pprint.pformat(st.session_state[f"{application}_visualizations"])
            # logger.debug(f"preloaded dictionary: \n{my_complex_dict}")
            
            for visuals in st.session_state[f"{application}_visualizations"]:
                if visuals['id'] not in except_ids:
                    with st.container(border=True):
                        kpi_query = visuals["kpi_query"]
                        st.text_input("Prompt:", value=visuals["kpi_query"], key=visuals["id"], on_change=visual_edit, args=(lida, textgen_config, visuals["id"], st.session_state["cidds_summary"], application))
                        if "visualizations_path" in visuals:
                            st.image(visuals["visualizations_path"], use_column_width="auto")
                            if is_diaplay_explability:
                                with st.expander("See explanation"):
                                    for description in visuals["visualizations_description"]:
                                        st.markdown(f"""**{description['section']}**""")
                                        st.write(description["explanation"])
                                        st.divider()
                        else:
                            st.warning(f"I am unable to generate visualtization for:{kpi_query}.")

def save_template(user_id, application, template_name):
    user_dict = dict()
    user_dict["user_id"] = user_id
    user_dict["Date_of_creation"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_dict["deereAI_model_ID"] = 1635
    user_dict["application"] = application
    KPI_list = copy.deepcopy(st.session_state[f"{application}_visualizations"])
    for items in KPI_list:
        if "visualizations" in items:
            del items["visualizations"]
    user_dict["KPI_list"] = KPI_list
    current_time = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    json_path = f"data/KPIs/{application}/{user_id}_{application}_{template_name}.json"
    with open(str(json_path), "w") as fp:
        json.dump(user_dict , fp, indent = 4) 
