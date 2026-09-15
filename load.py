import pandas as pd
from sqlalchemy import create_engine


engine=create_engine('postgresql://postgres:oussama123@localhost:5432/meteoetl')

df=pd.read_csv('gold/gold_data.csv')

df['date']=pd.to_datetime(df['date'])

df.to_sql('gold_data',con=engine,if_exists='replace',index=False)
