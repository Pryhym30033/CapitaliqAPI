
from matplotlib.ticker import FuncFormatter
from pandas import to_numeric
from pyparsing import alphas
from spgmi_api_sdk.ciq.services import SDKDataServices
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import questionary
from questionary import Style
import requests
import json
import os

from wcwidth import width

from capitaliq_client import response, bearer_token, payload, req_array

load_dotenv()

custom_style = Style([
    ('qmark', 'fg:#673ab7 bold'),
    ('question', 'bold'),
    ('answer', 'fg:#f44336 bold'),
    ('pointer', 'fg:#673ab7 bold'),
    ('highlighted', 'fg:#673ab7 bold'),
    ('selected', 'fg:#cc5454'),
    ('separator', 'fg:#cc5454'),
    ('instruction', ''),
    ('text', ''),
    ('disabled', 'fg:#858585 italic')
])

def quarter_only(x, pos):
    date = mdates.num2date(x)
    if date.month in [4, 7, 10]:         # show only Apr, Jul, Oct
        return date.strftime('%b')[0]    # single letter
    return ''


spg = SDKDataServices(username=os.getenv("CAPITALIQ_USER"), password=os.getenv("CAPITALIQ_PASS"))

def Company_List():
    name = input("Company Name: ")
    names = get_name(name)
    ciqs = getCIQ(name)

    menu = []
    for index, value in enumerate(names):
        menu.append(F"{value['Row'][0]} {ciqs[index]['Row'][0]}")

    selected = questionary.select(
            "Choose company:",
             choices=menu,
        pointer="→ ",
        use_shortcuts=True,
        use_indicator=False
    ).ask()
    return selected.rsplit(" ", 1)

def get_name(name):
    accessToken = spg.get_token().get('access_token')
    endpoint_url = "https://api-ciq.marketintelligence.spglobal.com/gdsapi/rest/v3/clientservice.json"

    bearer_token = accessToken
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {bearer_token}"
    }

    req_array = [
        {"function":"GDSHE","identifier":f"{name}","mnemonic":"IQ_COMPANY_NAME_QUICK_MATCH","properties":{"startrank":"1","endrank":"4"}},
    ]

    payload = {"inputRequests": req_array}

    response = requests.post(
        endpoint_url,
        headers=headers,
        data=json.dumps(payload)
    )
    response.raise_for_status()
    response_data = response.json()
    response_header = response_data['GDSSDKResponse'][0]
    return response_header['Rows']

def getCIQ(name):

    accessToken = spg.get_token().get('access_token')
    endpoint_url = "https://api-ciq.marketintelligence.spglobal.com/gdsapi/rest/v3/clientservice.json"

    bearer_token = accessToken
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {bearer_token}"
    }

    req_array = [
        {"function": "GDSHE", "identifier": f"{name}", "mnemonic": "IQ_COMPANY_ID_QUICK_MATCH", "properties": {"startrank": "1", "endrank": "4"}}
    ]

    payload = {"inputRequests": req_array}

    response = requests.post(
        endpoint_url,
        headers=headers,
        data=json.dumps(payload)
    )
    response.raise_for_status()
    response_data = response.json()
    response_header = response_data['GDSSDKResponse'][0]
    return response_header['Rows']


def GetFinData(ciq,stryr, endyr):
    numyrs = endyr - stryr+1
    yrs = str(numyrs)
    findata = spg.get_financials_historical(
        identifiers=[f"{ciq}"],
         mnemonics=[
             "IQ_PERIODDATE",
             "IQ_EBIT",
             "IQ_INC_TAX",
             "IQ_TOTAL_CA",
             "IQ_TOTAL_CL",
             "IQ_TOTAL_REV",
             "IQ_NPPE_EXCL_OPER_LEASES",
             "IQ_GW",
             "IQ_CAPEX",
             "IQ_LEVERED_FCF",
             "IQ_UNLEVERED_FCF",
             "IQ_DILUT_WEIGHT",
             "IQ_TOTAL_REV",
             "IQ_DILUT_EPS_EXCL"
         ],
        properties={
            "periodType": f"IQ_FY-{yrs}",
            "asOfDate": f"6/13/{endyr}",
            "currencyId": "USD",
            "currencyConversionModeId": "HISTORICAL",
        })
    return findata

def CashAccum(dataframe):
    finDate = pd.to_datetime(dataframe['IQ_PERIODDATE'], errors='coerce')
    cashFlow = pd.to_numeric(dataframe["IQ_UNLEVERED_FCF"], errors='coerce').fillna(0)
    shares = pd.to_numeric(dataframe["IQ_DILUT_WEIGHT"], errors='coerce').fillna(0)
    cshPerShare = cashFlow/shares
    accCash = cshPerShare.cumsum()
    cshflw = pd.DataFrame({
        "DATE": finDate,
        "CASHFLOW/SHARE": cshPerShare,
        "ACCUM CASH": accCash
    })
    return cshflw


def GetPriceData(ciq, stryr, endyr):
    market = spg.get_pricing_info_time_series(
        identifiers=[f"{ciq}"],
        properties={
            "frequency": "Monthly",
            "startDate": f"1/1/{stryr}",
            "endDate": f"1/1/{endyr}",
            "currencyId": "USD",
            "currencyConversionModeId": "HISTORICAL"
        })
    return market

def PriceAccum(pricedata):
    mrkDate = pd.to_datetime(pricedata['asOfDate'], errors='coerce')
    clsPrice = pd.to_numeric(pricedata['IQ_CLOSEPRICE'], errors='coerce').fillna(0)
    prices = pd.DataFrame({
        "DATE": mrkDate,
        "PRICE": clsPrice
    })
    return prices

def rev(dataframe):
    revenue = pd.to_numeric(dataframe['IQ_TOTAL_REV'], errors='coerce').fillna(0)
    finDate = pd.to_datetime(dataframe['IQ_PERIODDATE'], errors='coerce')
    shares = pd.to_numeric(dataframe["IQ_DILUT_WEIGHT"], errors='coerce').fillna(0)
    revPerShare = revenue/shares
    revFrame = pd.DataFrame({
        "DATE": finDate,
        "REVS": revPerShare
    })
    return revFrame

def ROIC(dataframe):

    nopat = pd.to_numeric(dataframe['IQ_EBIT'], errors="coerce").fillna(0) - pd.to_numeric(dataframe['IQ_INC_TAX'], errors='coerce').fillna(0)
    exCash = pd.to_numeric(dataframe['IQ_TOTAL_REV'], errors='coerce').fillna(0) * 0.01
    ic = (pd.to_numeric(dataframe['IQ_TOTAL_CA'], errors='coerce').fillna(0) - pd.to_numeric(dataframe['IQ_TOTAL_CL'], errors='coerce').fillna(0)) + pd.to_numeric(dataframe['IQ_NPPE_EXCL_OPER_LEASES'], errors='coerce').fillna(0) + pd.to_numeric(dataframe['IQ_GW'], errors='coerce').fillna(0) - exCash
    year = pd.to_datetime(dataframe['IQ_PERIODDATE'])

    ROIC = nopat/ic


    roic = pd.DataFrame({
        "DATE": year,
        'ROIC': ROIC,
        'NOPAT': nopat,
        'IC': ic
    })
    return roic





def Plot(name, findata, pricedata, revdata, roicdata):



    fig, ax = plt.subplots(figsize=(14, 5))
    ax2 = ax.twinx()

    ax2.plot(pricedata['DATE'], pricedata['PRICE'], marker='o', color='blue', linestyle='-')
    ax2.plot(findata['DATE'], findata['ACCUM CASH'], marker='x', color='orange', linestyle='-')
    ax2.plot(revdata['DATE'], revdata['REVS'], marker='v', color='red', linestyle='--')
    ax2.set_ylabel('/Share')

    ax.bar(roicdata['DATE'], roicdata['ROIC'],  color='indianred', width=20, alpha=0.3)
    ax.set_ylabel('Return %')


    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('\n%Y'))

    ax.xaxis.set_minor_locator(mdates.MonthLocator())
    ax.xaxis.set_minor_formatter(FuncFormatter(quarter_only))

    ax.set_title(f"{name}")
    ax.grid(True)
    plt.tight_layout()
    plt.show()

def report(name, roicframe, finframe, revframe):
    roics = round((roicframe['ROIC'].mean()*100), 1)
    csh = []
    revs = []
    for index, cshflws in enumerate(finframe['ACCUM CASH'].iloc[1:], start=1):
        perchange = (cshflws - finframe['ACCUM CASH'].iloc[index - 1])/finframe['ACCUM CASH'].iloc[index - 1]
        csh.append(perchange)

    for index, rev in enumerate(revframe['REVS'].iloc[1:], start=1):
        revchange = (rev - revframe['REVS'].iloc[index - 1]) / revframe['REVS'].iloc[index - 1]
        revs.append(revchange)

    period = round((finframe['ACCUM CASH'].iloc[-1] - finframe['ACCUM CASH'].iloc[0])/finframe['ACCUM CASH'].iloc[0]*100, 1)

    print(f"""
    Company Name: {name}
    AVG ROIC: {roics}%
    AVG FCF GROWTH: {round(np.mean(csh*100), 1)}%
    FCF GROWTH FOR PERIOD: {period}%
    AVG REVENUE GROWTH: {round(np.mean(revs*100), 1)}%
""")

