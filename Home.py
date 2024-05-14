import streamlit as st
import src.st_utils as st_utils
import pprint
import logging
from logging.config import fileConfig
import configparser
#from dotenv import load_dotenv
from lida import Manager, TextGenerationConfig, llm
import time

# BEGIN-1: Okta OIDC Addition:
import os

#load_dotenv()

fileConfig('config/logging_config.ini')
logger = logging.getLogger()
# Initialize Streamlit app settings

is_diaplay_explability = True
st.set_page_config(page_title="Business & IT Operations Network Dashboard", layout="wide", page_icon="📊")
st.title("Business & IT Operations Network Dashboard")


config = configparser.ConfigParser()



st.write("")
Input = """
Business & IT Operations Network Dashboard, powered by LLM, is a comprehensive tool designed for the automatic generation of 
visualizations and infographics. It seamlessly integrates with various software systems, including Worksoft CTM 
and Checkmarx, to provide detailed insights and analytics.
This dashboard provides users with a comprehensive view of their software testing and security processes. 
This empowers teams to make informed decisions, streamline workflows, and drive continuous improvement across 
their application development lifecycle.
 
"""
def stream_data():
    for word in Input.split(" "):
        yield word + " "
        time.sleep(0.01)
st.write_stream(stream_data)