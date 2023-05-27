#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from flask import Flask, request, jsonify
import requests
import json
import xmltodict
from collections import OrderedDict
import pandas as pd
from flask_cors import CORS

df = pd.read_csv('list_50.csv')
df_event= pd.read_csv('aaa .csv')
app = Flask(__name__)

CORS(app, resources={r'*': {'origins': ['https://seoul-weather-fe.vercel.app/', 'http://localhost:3000']}})

def get_api(gu):
    if gu == '강동구':
        gu = '송파구'
    elif gu == '강서구' or gu == '양천구':
        gu = '영등포구'
    elif gu =='동대문구':
        gu = '중구'
    elif gu == '성북구':
        gu = '종로구'
    elif gu =='중랑구':
        gu = '광진구'
    elif gu =='서대문구':
        gu = '종로구'
    
    #공공데이터 api 요청
    name = df[df['구'] == gu]['장소명'].values[0]
    url = 'http://openapi.seoul.go.kr:8088/6351784378646a663631754e72636a/xml/citydata/1/5/' + name
    response = requests.get(url)
    jsonR = json.dumps(xmltodict.parse(response.text), indent = 4)
    data = json.loads(jsonR)
    
    return data

@app.route('/user/<gu>')
def get_main(gu):
    data = get_api(gu)
    
    #데이터 가공
    gu = data['SeoulRtd.citydata']['CITYDATA']['COVID_19_STTS']['COVID_19_STTS']["GU_NM"]
    temp = data['SeoulRtd.citydata']['CITYDATA']['WEATHER_STTS']['WEATHER_STTS']['TEMP']
    sensible_tmp = data['SeoulRtd.citydata']['CITYDATA']['WEATHER_STTS']['WEATHER_STTS']['SENSIBLE_TEMP']
    sky_stts = data['SeoulRtd.citydata']['CITYDATA']['WEATHER_STTS']['WEATHER_STTS']['FCST24HOURS']['FCST24HOURS'][0]['SKY_STTS']
    #최고/최저
    max_tmp = data['SeoulRtd.citydata']['CITYDATA']['WEATHER_STTS']['WEATHER_STTS']['MAX_TEMP']
    min_tmp = data['SeoulRtd.citydata']['CITYDATA']['WEATHER_STTS']['WEATHER_STTS']['MIN_TEMP']
    #강수량
    rain_pre = data['SeoulRtd.citydata']['CITYDATA']['WEATHER_STTS']['WEATHER_STTS']['PRECIPITATION']
    #미세먼지, 초미세먼지
    pm10 = data['SeoulRtd.citydata']['CITYDATA']['WEATHER_STTS']['WEATHER_STTS']['PM10']
    pm25 = data['SeoulRtd.citydata']['CITYDATA']['WEATHER_STTS']['WEATHER_STTS']['PM25']
    #풍속
    wind = data['SeoulRtd.citydata']['CITYDATA']['WEATHER_STTS']['WEATHER_STTS']['WIND_SPD']
    #일출, 일몰 
    sunset = data['SeoulRtd.citydata']['CITYDATA']['WEATHER_STTS']['WEATHER_STTS']['SUNSET']
    sunrise = data['SeoulRtd.citydata']['CITYDATA']['WEATHER_STTS']['WEATHER_STTS']['SUNRISE']
    #자외선
    uv = data['SeoulRtd.citydata']['CITYDATA']['WEATHER_STTS']['WEATHER_STTS']['UV_INDEX']
    humiditiy = data['SeoulRtd.citydata']['CITYDATA']['WEATHER_STTS']['WEATHER_STTS']['HUMIDITY']
    
    item = []
    if int(pm10) > 81 or int(pm25) > 35:
        item.append('mask')
    if rain_pre != '-':
        item.append('unbrella')
    if sky_stts == '맑음':
        item.append('sunglass')
    if uv == '높음':
        item.append('suncream')
    
    main_data = OrderedDict()
    main_data['sensible_tmp'] = sensible_tmp
    main_data["gu"] = gu
    main_data["temp"] = temp
    main_data["sky_stts"] = sky_stts
    main_data['max_tmp'] = max_tmp
    main_data['min_tmp'] = min_tmp
    main_data['rain_pre'] = rain_pre
    main_data['pm10'] = pm10
    main_data['pm25'] = pm25
    main_data['wind'] = wind
    main_data['sunset'] = sunset
    main_data['sunrise'] = sunrise
    main_data['uv'] = uv
    main_data['humiditiy'] = humiditiy 
    main_data['item'] = item
    
    return json.dumps(main_data, ensure_ascii=False, indent="\t")
    
    
@app.route('/user/precpt/<gu>')
def get_precpt(gu):
    data = get_api(gu)
    
    weather = data['SeoulRtd.citydata']['CITYDATA']['WEATHER_STTS']['WEATHER_STTS']['FCST24HOURS']['FCST24HOURS']
    
    return json.dumps(weather, ensure_ascii=False, indent="\t")

@app.route('/user/event/<gu>')
def get_event(gu):
    dataset = []
    api = get_api(gu)
    weather = api['SeoulRtd.citydata']['CITYDATA']['WEATHER_STTS']['WEATHER_STTS']['PRECPT_TYPE']
    df_event2 = df_event[df_event['자치구']==gu]
    if weather == '비':
        act = df_event2[df_event2['실내'] == '실내']
    for index, row in act.iterrows():
        data = {}
        data['공연/행사명'] = row['공연/행사명']
        data['분류'] = row['분류']
        data['날짜/시간'] = row['날짜/시간']
        data['프로그램소개'] = row['프로그램소개']
        data['홈페이지주소'] = row['홈페이지?주소']
        dataset.append(data)
    return json.dumps(dataset, ensure_ascii=False, indent="\t")


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False, port=5001)


# In[ ]:




