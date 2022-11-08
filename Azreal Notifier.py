import streamlit as st

from smtplib import SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from pretty_html_table import build_table

from datetime import datetime

from tvDatafeed import TvDatafeed, Interval
import numpy as np
import pandas as pd
import pandas_ta as ta

import time

def FEMUR():
    Forex_Pairs_List = ["EURUSD","USDJPY","GBPUSD","AUDUSD","USDCHF","NZDUSD","USDCAD",
                       "EURJPY","EURGBP","EURAUD","EURCHF","EURNZD","EURCAD",
                       "GBPJPY","CHFJPY","NZDJPY","AUDJPY","CADJPY",
                       "GBPAUD","AUDCHF","AUDNZD","AUDCAD",
                       "GBPCHF","NZDCHF","CADCHF",
                       "GBPNZD","GBPCAD",
                       "NZDCAD"]

    Final_df = pd.DataFrame()

    username = 'Azreal1'
    password = 'Mynameisdhruv123!@#'

    tv = TvDatafeed(username, password)

    for Currency_Pair in Forex_Pairs_List:
        Symbol_String = Currency_Pair
        Currency_Pair = tv.get_hist(symbol = 'FX:{}'.format(Currency_Pair), exchange = 'FXCM',
                                    interval = Interval.in_1_hour, n_bars = 100)
        #Stochastic
        Stoch = round(ta.stoch(high = Currency_Pair["high"], low = Currency_Pair["low"], 
                               close = Currency_Pair["close"], window = 14, smooth_window = 3),2)
        Currency_Pair["Stochastic %K"] = Stoch["STOCHk_14_3_3"]
        Currency_Pair["Stochastic %D"] = Stoch["STOCHd_14_3_3"]
        #Heiken Ashi
        if Symbol_String[-3:] == "JPY":
            Rounding = 3
        else:
            Rounding = 5
        Heiken_Ashi = round(ta.ha(Currency_Pair["open"], high = Currency_Pair["high"], 
                                  low = Currency_Pair["low"], close = Currency_Pair["close"]),Rounding)
        Currency_Pair["Heiken Ashi Open"] = Heiken_Ashi["HA_open"]
        Currency_Pair["Heiken Ashi High"] = Heiken_Ashi["HA_high"]
        Currency_Pair["Heiken Ashi Low"] = Heiken_Ashi["HA_low"]
        Currency_Pair["Heiken Ashi Close"] = Heiken_Ashi["HA_close"]

        #Heiken Ashi Bool
        Heiken_Ashi_Boolean = []

        i = 0
        while i < Currency_Pair.shape[0]:
            if (Currency_Pair["Heiken Ashi Close"][i] - Currency_Pair["Heiken Ashi Open"][i]) >= 0:
                Heiken_Ashi_Boolean.append(1)
            elif(Currency_Pair["Heiken Ashi Close"][i] - Currency_Pair["Heiken Ashi Open"][i]) < 0:
                Heiken_Ashi_Boolean.append(0)
            i+=1
        Currency_Pair["Heiken Ashi Boolean"] = Heiken_Ashi_Boolean
        Currency_Pair = Currency_Pair.iloc[15:,:]
        
        # Peak swing high and low calculations
        Peak_Value = []
        Peak_Stochastic_Value = []
        Peak_Value_List = list()
        Peak_Stochastic_Value_List = list()
        Peak_Value_List = [np.nan]*Currency_Pair.shape[0]
        Peak_Stochastic_Value_List = [np.nan]*Currency_Pair.shape[0]

        i = 0

        while i < Currency_Pair.shape[0] - 1:
            if Currency_Pair["Heiken Ashi Boolean"][i] == 1 and Currency_Pair["Heiken Ashi Boolean"][i+1] == 0:
                Peak_Value.append(Currency_Pair["close"][i])
                Peak_Stochastic_Value.append(Currency_Pair["Stochastic %K"][i])
                j = i
                while Currency_Pair["Heiken Ashi Boolean"][j] == 1:
                    Peak_Value.append(Currency_Pair["close"][j])
                    Peak_Stochastic_Value.append(Currency_Pair["Stochastic %K"][j])
                    j-=1
                Max_Value = max(Peak_Value)
                Max_Stochastic_Value = max(Peak_Stochastic_Value)
                Peak_Value = []
                Peak_Stochastic_Value = []
                Peak_Value_List[i+1] = Max_Value
                Peak_Stochastic_Value_List[i+1] = Max_Stochastic_Value
                i+=1
            elif Currency_Pair["Heiken Ashi Boolean"][i] == 0 and Currency_Pair["Heiken Ashi Boolean"][i+1] == 1:
                Peak_Value.append(Currency_Pair["close"][i])
                Peak_Stochastic_Value.append(Currency_Pair["Stochastic %K"][i])
                j = i
                while Currency_Pair["Heiken Ashi Boolean"][j] == 0:
                    Peak_Value.append(Currency_Pair["close"][j])
                    Peak_Stochastic_Value.append(Currency_Pair["Stochastic %K"][j])
                    j-=1
                Min_Value = min(Peak_Value)
                Min_Stochastic_Value = min(Peak_Stochastic_Value)
                Peak_Value = []
                Peak_Stochastic_Value = []
                Peak_Value_List[i+1] = Min_Value
                Peak_Stochastic_Value_List[i+1] = Min_Stochastic_Value
                i+=1
            elif Currency_Pair["Heiken Ashi Boolean"][i] == 1 and Currency_Pair["Heiken Ashi Boolean"][i+1] == 1:
                i+=1
            elif Currency_Pair["Heiken Ashi Boolean"][i] == 0 and Currency_Pair["Heiken Ashi Boolean"][i+1] == 0:
                i+=1

        Currency_Pair["Peak Value"] = Peak_Value_List
        Currency_Pair["Stochastic Peak Value"] = Peak_Stochastic_Value_List

        Swing_High_Recent = np.nan
        Stochastic_High_Recent = np.nan
        Swing_Low_Recent = np.nan
        Stochastic_Low_Recent = np.nan

        Looking_For_Shorts = np.nan
        Looking_For_Longs = np.nan

        Divergence_List = list()
        Divergence_List = [np.nan]*Currency_Pair.shape[0]

        i = 0

        while i < Currency_Pair.shape[0] - 1:
          if (pd.isna(Currency_Pair["Peak Value"][i]) == False and Currency_Pair["Heiken Ashi Boolean"][i] == 1):
              Swing_Low_Recent = Currency_Pair["Peak Value"][i]
              Stochastic_Low_Recent = Currency_Pair["Stochastic Peak Value"][i]
              Looking_For_Shorts = True
              Looking_For_Longs = False
              i+=1
          elif (pd.isna(Currency_Pair["Peak Value"][i]) == False and Currency_Pair["Heiken Ashi Boolean"][i] == 0):
              Swing_High_Recent = Currency_Pair["Peak Value"][i]
              Stochastic_High_Recent = Currency_Pair["Stochastic Peak Value"][i]
              Looking_For_Shorts = False
              Looking_For_Longs = True
              i+=1
          if (pd.isna(Swing_High_Recent) == False and pd.isna(Swing_Low_Recent) == False):
            if (Looking_For_Shorts == True):
              if(Currency_Pair["close"][i] >= Swing_High_Recent and Currency_Pair["Stochastic %K"][i] <= Stochastic_High_Recent):
                Divergence_List[i] = "Regular Divergence Short"
                i+=1
              elif(Currency_Pair["close"][i] <= Swing_High_Recent and Currency_Pair["Stochastic %K"][i] >= Stochastic_High_Recent):
                Divergence_List[i] = "Hidden Divergence Short"
                i+=1
              else:
                i+=1
            elif (Looking_For_Longs == True):
                if(Currency_Pair["close"][i] <= Swing_Low_Recent and Currency_Pair["Stochastic %K"][i] >= Stochastic_Low_Recent):
                  Divergence_List[i] = "Regular Divergence Long"
                  i+=1
                elif(Currency_Pair["close"][i] >= Swing_Low_Recent and Currency_Pair["Stochastic %K"][i] <= Stochastic_Low_Recent):
                  Divergence_List[i] = "Hidden Divergence Long"
                  i+=1
                else:
                  i+=1
          else:
            i+=1

        Currency_Pair["Divergence"] = Divergence_List

        Final_df = pd.concat([Final_df , Currency_Pair.iloc[[-2]]])
    Final_df = Final_df.drop(["open","high","low","close","volume","Heiken Ashi Open","Heiken Ashi High","Heiken Ashi Low","Heiken Ashi Close"
    ,"Heiken Ashi Boolean","Stochastic %K","Stochastic %D","Peak Value","Stochastic Peak Value"], axis = 1)
    return Final_df

def send_mail(body):
    message = MIMEMultipart()
    message['Subject'] = 'Azreal Update'
    message['From'] = 'dhruv.suresh2@gmail.com'
    message['To'] = 'f20180884g@alumni.bits-pilani.ac.in'

    body_content = body
    message.attach(MIMEText(body_content, "html"))
    msg_body = message.as_string()

    server = SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(message['From'], 'nterwjjlblthqkri')
    server.sendmail(message['From'], message['To'], msg_body)
    server.quit()

st.title("Notification Engine")

while True:
    Output = FEMUR()
    Index_list = list(Output.index.values)
    Recent_Open_Time = Index_list[0]
    Current_Time = np.datetime64(datetime.now())
    x = Current_Time - Recent_Open_Time
    delta_s = x.astype('timedelta64[s]').astype(np.int64)
    Waiting_time = 7210 - delta_s
    time.sleep(Waiting_time)
    Output = FEMUR()
    mail_output = build_table(Output, 'blue_light')
    send_mail(mail_output)
