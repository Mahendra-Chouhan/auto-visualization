import json
import pandas as pd


def main(response, account_list):
    json_string = json.dumps(response.to_dict(), default=str)
    transactions = json.loads(json_string)["transactions"]
    df = pd.DataFrame.from_dict(transactions)

    df.drop(columns=['account_owner', 'authorized_date', "authorized_datetime", "category_id",
                    "datetime", "location", "logo_url", "merchant_entity_id", "name", 
                    "check_number", "counterparties", "payment_meta", "payment_meta", "pending", "pending_transaction_id", 
                    "personal_finance_category", "personal_finance_category_icon_url", "transaction_code", "transaction_id", "transaction_type",
                    "unofficial_currency_code", "website"], inplace=True, errors="ignore")
    if "category" in df:
        df["category"], df["Sub-category"] = [str(catagory[-1]) if len(catagory) > 0 else None for catagory in df["category"] ], [str(catagory[-2]) if len(catagory) > 1 else None for catagory in df["category"]]
    if "account_id" in df:
        accounts, account_type, account_sub_type  = {}, {}, {}
        df["account_type"], df["account_subtype"] = df["account_id"], df["account_id"]
        for account_id in df['account_id'].unique():
            for account in account_list:
                if account["account_id"] == account_id:
                    accounts[account_id] = str(account["name"])
                    account_type[account_id] = str(account["type"])
                    account_sub_type[account_id] = str(account["subtype"])

        df.replace({'account_id': accounts}, inplace=True)
        df.replace({'account_type': account_type}, inplace=True)
        df.replace({'account_subtype': account_sub_type}, inplace=True)
        df.rename(columns={"account_id": "account"}, inplace=True)


    return df

if __name__ == "__main__":
    pass
