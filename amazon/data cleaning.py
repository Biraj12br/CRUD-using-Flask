import numpy as np
import pandas as pd

df=pd.read_csv('amazon sales.csv')

print(df.columns)
""" 'product_id', 'product_name', 'category', 'discounted_price',
       'actual_price', 'discount_percentage', 'rating', 'rating_count',
       'about_product', 'user_id', 'user_name', 'review_id', 'review_title',
       'review_content', 'img_link', 'product_link' """

df['discount_percentage']=df['discount_percentage'].str.replace('%','').astype(float)
df['discount_percentage']=df['discount_percentage']/100


df['discounted_price'] = df['discounted_price'].str.replace("₹",'')
df['discounted_price'] = df['discounted_price'].str.replace(",",'')
df['discounted_price'] = df['discounted_price'].astype(float)


df['actual_price'] = df['actual_price'].str.replace("₹",'')
df['actual_price'] = df['actual_price'].str.replace(",",'')
df['actual_price'] = df['actual_price'].astype(float)


df['rating'] = df['rating'].str.replace('|', '3.9').astype(float)

df['rating_count'] = df['rating_count'].str.replace(',', '').astype(float)

value=df['rating_count'].median()
df['rating_count'].fillna(value)

print(df.duplicated().any())

print(df.info())






