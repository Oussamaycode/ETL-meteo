from airflow.sdk import dag, task
from sqlalchemy import create_engine
import pendulum
import pandas as pd
import requests


@dag(
    dag_id="meteo_etl",
    schedule="0 0 * * *",
    start_date=pendulum.datetime(2026, 9, 18, tz="Africa/Casablanca"),
    catchup=False,
)
def meteo_etl():

    @task
    def extract():

        def get_weather(latitude, longitude):
            url = "https://api.open-meteo.com/v1/forecast"

            params = {
                "latitude": ",".join(map(str, latitude)),
                "longitude": ",".join(map(str, longitude)),
                "daily": [
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "precipitation_sum",
                    "precipitation_probability_max",
                    "wind_speed_10m_max",
                    "wind_gusts_10m_max",
                    "weather_code"
                ],
                "forecast_days": 7,
                "timezone": "auto"
            }

            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()


        def weather_to_df(data):
            records = []
            for loc in data:
                daily = loc["daily"]
                n_days = len(daily["time"])
                for i in range(n_days):
                    records.append({
                        "lat": loc["latitude"],
                        "lng": loc["longitude"],
                        "date": daily["time"][i],
                        "temperature_2m_max": daily["temperature_2m_max"][i],
                        "temperature_2m_min": daily["temperature_2m_min"][i],
                        "precipitation_sum": daily["precipitation_sum"][i],
                        "precipitation_probability_max": daily["precipitation_probability_max"][i],
                        "wind_speed_10m_max": daily["wind_speed_10m_max"][i],
                        "wind_gusts_10m_max": daily["wind_gusts_10m_max"][i],
                        "weather_code": daily["weather_code"][i],
                    })
            return pd.DataFrame(records)


        cities = pd.read_csv("/opt/airflow/data.csv")

        data = get_weather(cities["lat"].tolist(), cities["lng"].tolist())
        df = weather_to_df(data)

        print(df)

        df.to_csv("/opt/airflow/data/bronze/raw.csv",index=False)   


    @task
    def transform():

        df=pd.read_csv("/opt/airflow/data/bronze/raw.csv")
        cities=pd.read_csv("/opt/airflow/data.csv",thousands=',')

        def doublan():
            print("total doublan:", df.duplicated().sum())



        def  incoherance():
            incoherance=0
            a=df[(df["temperature_2m_max"]<0) | (df["temperature_2m_min"]<0)]
            if(a.size>0):
                incoherance+=1
                print("incoherance detecté:temperature negatif")

            b=df[df["temperature_2m_max"]<df["temperature_2m_min"]]
            if(b.size>0):
                    incoherance+=1
                    print("incoherance detecté:temperature min>temperature max")

            c=df[df["precipitation_sum"]<0]
            if(c.size>0):
                    incoherance+=1
                    print("incoherance detecté:precipitation negative")

            d=df[(df["precipitation_probability_max"]<0)| (df["precipitation_probability_max"]>100)]
            if(d.size>0):
                    incoherance+=1
                    print("incoherance detecté:probabiltés invalides")

            e=df[df["wind_speed_10m_max"]<0]
            if(e.size>0):
                        incoherance+=1
                        print("incoherance detecté:vitesse de vent negatives")

            f=df[df["wind_gusts_10m_max"]<0]
            if(f.size>0):
                        incoherance+=1
                        print("incoherance detecté:refales negatives")

            print("total incoherance:",incoherance)

        def standerize():
                
                df['date']=pd.to_datetime(df['date'])

                df['precipitation_probability_max']=pd.to_numeric(df['precipitation_probability_max'])

                df['precipitation_sum']=pd.to_numeric(df['precipitation_sum'])

                df['temperature_2m_max']=pd.to_numeric(df['temperature_2m_min'])

                df['temperature_2m_min']=pd.to_numeric(df["temperature_2m_min"])

                df['wind_gusts_10m_max']=pd.to_numeric(df['wind_gusts_10m_max'])

                df["wind_speed_10m_max"]=pd.to_numeric(df['wind_speed_10m_max'])

                df["lat"] = pd.to_numeric(cities["lat"].repeat(7).values)
                df["lng"] = pd.to_numeric(cities["lng"].repeat(7).values)




            
        def join_cities():

            df1=pd.merge(cities[['city', 'lat', 'lng']],df, on=['lat', 'lng'], how='left')
            df1.to_csv("/opt/airflow/data/silver/silver_data.csv",index=False)


        def categories():
            df1=pd.read_csv("/opt/airflow/data/silver/silver_data.csv")
            df1['temperature_category']=pd.cut(
                df1['temperature_2m_max'],
                bins=[-float("inf"),10,20,30,35,float("inf")],
                labels= [
                "Froide",
                "Fraîche",
                "Normale",
                "Chaude",
                "Très chaude"
                ]
            )
            df1['precipitation_category']=pd.cut(
                df1['precipitation_sum'],
                bins=[-0.01,0,5,20,50,float('inf')],
                labels=[               
                    "Aucune",
                    "Faible",
                    "Modéréé",
                    "Forte",
                    "Trés Forte"
                ]
            )

            df1['wind_category']=pd.cut(
                df1['wind_speed_10m_max'],
                bins=[-float("inf"), 20, 40, 60, float("inf")],
                labels=[
                    "Faible",
                    "Modéré",
                    "Fort",
                    "Très fort"
                ]
            )


            df1.to_csv('/opt/airflow/data/gold/gold_data.csv',index=False)

        def risk():

            df1=pd.read_csv('/opt/airflow/data/gold/gold_data.csv')

            precipitation_score = {
                "Aucune": 0,
                "Faible": 1,
                "Modéré": 2,
                "Fort": 3,
                "Très fort": 4
            }

            wind_score = {
                "Faible": 0,
                "Modéré": 1,
                "Fort": 2,
                "Très fort": 3
            }

            temp_score={
                "Froide":0,
                "Fraîche":1,
                "Normale":2,
                "Chaude":2,
                "Très chaude":3
            }

            
            df1['risk_score']= df1['precipitation_category'].map(precipitation_score)*10+df1['wind_category'].map(wind_score)*10+df1['temperature_category'].map(temp_score)*10
            df1['risk_score'].fillna(df1['risk_score'].mean())
            df1.to_csv('/opt/airflow/data/gold/gold_data.csv',index=False)
                
                
                
            
          

            doublan()
            incoherance()
            standerize()
            join_cities()
            categories()
            risk()


    @task
    def load_postgres():
        engine = create_engine('postgresql://airflow:airflow@postgres:5432/meteo_data')

        df=pd.read_csv('/opt/airflow/data/gold/gold_data.csv')

        df['date']=pd.to_datetime(df['date'])

        df.to_sql('meteo_data',con=engine,if_exists='replace',index=False)


    extract_task = extract()
    transform_task=transform()
    load_task = load_postgres()


    extract_task >> transform_task >> load_task


meteo_etl()