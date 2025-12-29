import pandas as pd
from sqlalchemy import create_engine

df=pd.read_csv('final_amazon_sales.csv')

database_url='mysql://root:Biraj351@localhost/flask'

engine=create_engine(database_url)

try:
    df.to_sql(
        name='sales',          # Name of the SQL table
        con=engine,            # The SQLAlchemy connection/engine
        if_exists='replace',   # Options: 'fail', 'replace', 'append'
        index=False            # Do not write the DataFrame index as a column
    )
    print("Data imported successfully")

except Exception as e:
    print(f"The error is {e}")