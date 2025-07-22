# Import python packages
import streamlit as st
# from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
import requests

# new scetion to display nutrition information
smoothiefroot_response = requests.get("https://fruityvice.com/api/fruit/watermelon")
st.text(smoothiefroot_response.json())
sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

# Title and subtitle
st.title(f":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Order name
name_on_order = st.text_input("Name on Smoothie:")
st.write('The name on your order will be: ', name_on_order)

# Establish Snowflake Connecton
cnx = st.connection("snowflake")
session = cnx.session()

# Get ingredients list
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
# The below line displays a table table
# st.dataframe(data=my_dataframe, use_container_width=True)

# Ingredients selections and order capture
ingredients_list = st.multiselect('Choose upto 5 ingredients: ',
                                  my_dataframe,
                                  max_selections=5)
if ingredients_list:
    ingredients_string = ''
    # st.write(ingredients_list)
    # st.text(ingredients_list)

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
    # st.write(ingredients_string)
    
    my_insert_stmt = """ insert into smoothies.public.orders (ingredients, name_on_order)
            values ('""" + ingredients_string + """', '""" + name_on_order + """')"""
    #st.write(my_insert_stmt)

    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered, '+name_on_order+'!', icon='✅')
