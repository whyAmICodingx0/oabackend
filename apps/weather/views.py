from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import datetime, timedelta
import requests

def get_latest_3hr_block_time():
    now = datetime.now()
    # 取最近 <= 現在小時的 3 的倍數
    hour_block = now.hour - (now.hour % 3)
    result = now.replace(hour=hour_block, minute=0, second=0, microsecond=0)
    return result

class homeWeatherView(APIView):
    def get(self, request):
        base_url = 'https://opendata.cwa.gov.tw'
        url = base_url + '/api/v1/rest/datastore/F-D0047-089'
        weatherIcon_url = 'https://www.cwa.gov.tw/V8/assets/img/weather_icons/weathers/svg_icon/day/'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/122.0.0.0 Safari/537.36',
            'accept': 'application/json'
        }
        params = {
            'Authorization': settings.CWA_API_KEY,
            'format': 'JSON',
            'ElementName': '溫度,天氣現象,3小時降雨機率',
            'LocationName': '臺中市',
        }
        response = requests.get(url, params=params, headers=headers)
        data_json = response.json()
        # if data_json:
        #     return Response(data_json)
        results = []
        now = datetime.now().replace(minute=0, second=0, microsecond=0)
        for i in data_json['records']['Locations'][0]['Location']:
            area = i['LocationName']
            for element in i['WeatherElement']:
                element_name = element['ElementName']
                for time_block in element['Time']:
                    if 'DataTime' in time_block:
                        now_time = now.strftime("%Y-%m-%dT%H:%M:%S")
                        block_time = time_block['DataTime'].replace('+08:00', '')
                    elif 'StartTime' in time_block:
                        now_time = get_latest_3hr_block_time().strftime("%Y-%m-%dT%H:%M:%S")
                        block_time = time_block['StartTime'].replace('+08:00', '')
                    else:
                        continue
                    if now_time <= block_time:
                        for value_dict in time_block['ElementValue']:
                            for key, value in value_dict.items():
                                try:
                                    value = int(value)
                                except ValueError:
                                    continue
                                if element_name == '天氣現象':
                                    value = weatherIcon_url + str(value).zfill(2) + '.svg'
                                results.append({
                                    "area": area,
                                    "element": element_name,
                                    "value": value
                                })
                        break

        return Response(results)

class weatherView(APIView):
    def get(self, request):
        city = request.query_params.get('city')
        print(city)
        base_url = 'https://opendata.cwa.gov.tw'
        url = base_url + '/api/v1/rest/datastore/F-D0047-089'
        weatherIcon_url = 'https://www.cwa.gov.tw/V8/assets/img/weather_icons/weathers/svg_icon/day/'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/122.0.0.0 Safari/537.36',
            'accept': 'application/json'
        }
        params = {
            'Authorization': settings.CWA_API_KEY,
            'format': 'JSON',
            'ElementName': '溫度,體感溫度,天氣現象',
            'LocationName': city,
        }
        response = requests.get(url, params=params, headers=headers)
        data_json = response.json()
        results = {}
        now = datetime.now().replace(minute=0, second=0, microsecond=0)
        for element in data_json['records']['Locations'][0]['Location'][0]['WeatherElement']:
            element_name = element['ElementName']
            results[element_name] = []
            for time_block in element['Time']:
                if 'DataTime' in time_block:
                    now_time = now.replace(minute=0, second=0, microsecond=0)
                    block_time = time_block['DataTime'].replace('+08:00', '')
                elif 'StartTime' in time_block:
                    now_time = get_latest_3hr_block_time()
                    block_time = time_block['StartTime'].replace('+08:00', '')
                else:
                    continue
                new_block_time = datetime.fromisoformat(block_time)
                one_day_range = now_time + timedelta(days=1)
                if new_block_time == one_day_range:
                    break
                if now_time <= new_block_time:
                    for value_dict in time_block['ElementValue']:
                        for key, value in value_dict.items():
                            try:
                                value = int(value)
                            except ValueError:
                                continue
                            if element_name == '天氣現象':
                                value = weatherIcon_url + str(value).zfill(2) + '.svg'
                            results[element_name].append({"time": new_block_time, "value": value})


        return Response(results)