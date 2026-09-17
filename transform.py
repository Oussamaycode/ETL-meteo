import pandas as pd

df=pd.read_csv("bronze/raw.csv")
cities=pd.read_csv("data.csv",thousands=',')

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

        df['lat']=pd.to_numeric(cities['lat'])

        df['lng']=pd.to_numeric(cities['lng'])




    
def join_cities():

    df1=pd.merge(cities[['city', 'lat', 'lng']],df, on=['lat', 'lng'], how='left')
    df1.to_csv("silver/silver_data.csv",index=False)
    print(df1.dtypes)

def categories():
    df1=pd.read_csv("silver/silver_data.csv")
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


    df1.to_csv('gold/gold_data.csv',index=False)

def risk():

    df1=pd.read_csv('gold/gold_data.csv')

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
    df1.to_csv('gold/gold_data.csv',index=False)
         
           
           
    
               

doublan()
incoherance()
standerize()
join_cities()
categories()
risk()
