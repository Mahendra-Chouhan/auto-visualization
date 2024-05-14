import plaid
from plaid.api import plaid_api
import json
import os
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest
from plaid.model.products import Products
import datetime as dt
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.accounts_get_request import AccountsGetRequest

clientId = os.environ["PLAID_CLIENT_ID"]
secret = os.environ["PLAID_SECRET"]

configuration = plaid.Configuration(
    host=plaid.Environment.Sandbox,
    api_key={
        'clientId': clientId,
        'secret': secret,
    }
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)


def get_access_token():
    pt_request = SandboxPublicTokenCreateRequest(
    institution_id="ins_109508",
    initial_products=[Products('transactions')])

    pt_response = client.sandbox_public_token_create(pt_request)

    # the public token is received from Plaid Link
    exchange_request = ItemPublicTokenExchangeRequest(
        public_token=pt_response['public_token']
    )
    exchange_response = client.item_public_token_exchange(exchange_request)
    os.environ["PLAID_BEARER_TOKEN"] =  exchange_response['access_token']
    
    

def get_accounts():
    access_token = os.getenv('PLAID_BEARER_TOKEN', None)
    ag_request = AccountsGetRequest(
        access_token=access_token
    )

    accounts_response = client.accounts_get(ag_request)
    accounts = accounts_response["accounts"]
    print(accounts)
    return accounts


def get_transactions(account_names, start_date, end_date, account_list):
    end_date = dt.date.today()
    start_date = (end_date - dt.timedelta(days=(365*2)))
    print(account_names)
    access_token = os.getenv('PLAID_BEARER_TOKEN', None)
    # account_list = get_accounts()
    account_ids = []
    for account in account_list:
        if account["name"] in account_names:
            account_ids.append(account["account_id"])

    print(account_ids)
    # DOWNLOADING JSON FOR TENANT ID #########################3
    
    options = TransactionsGetRequestOptions()
    options.account_ids = account_ids
    request = TransactionsGetRequest(
                access_token=access_token,
                start_date=start_date,
                end_date=end_date,
                options=options
            )
            

    response = client.transactions_get(request)
    transactions = response['transactions']

    while len(transactions) < response['total_transactions']:
        request = TransactionsGetRequest(
                access_token=access_token,
                start_date=start_date,
                end_date=end_date,
                options=TransactionsGetRequestOptions(
                    offset=len(transactions)
                )
    )
        response = client.transactions_get(request)
        transactions.extend(response['transactions'])

    response['transactions'] = transactions
    return response
