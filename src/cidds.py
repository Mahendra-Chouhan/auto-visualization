import requests
import json
import math
import urllib3
import os
import logging
from decouple import config 

logger = logging.getLogger()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_worksoft_details(tenant_Id, start_date, end_date, user_id, file_name):
    # DOWNLOADING JSON FOR TENANT ID #########################3
    pass
