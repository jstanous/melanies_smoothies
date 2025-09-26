# Import python packages
import streamlit as st
# from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Title and subtitle
st.title(f":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Order name
name_on_order = st.text_input("Name on Smoothie:")
st.write('The name on your order will be: ', name_on_order)

# Establish Snowflake Connecton
cnx = st.connection("snowflake")
session = cnx.session()
# Adding block to diagnose connections issues.
# st.write("Role:", session.get_current_role())
# st.write("Database:", session.get_current_database())
# st.write("Schema:", session.get_current_schema())

# Get ingredients list
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
# The below line displays a table table
# st.dataframe(data=my_dataframe, use_container_width=True)
pd_df = my_dataframe.to_pandas()
# st.dataframe(pd_df)
# st.stop()


# Ingredients selections and order capture
fruit_list = my_dataframe.to_pandas()['FRUIT_NAME'].tolist()
ingredients_list = st.multiselect('Choose up to 5 ingredients:', fruit_list, max_selections=5)

if ingredients_list:
    ingredients_string = ''
    # st.write(ingredients_list)
    # st.text(ingredients_list)

    time_to_insert = st.button('Submit Order')

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
# new section to display nutrition information
        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get("https://fruityvice.com/api/fruit/" + fruit_chosen)
        fruit_data = smoothiefroot_response.json()
        nutrients = fruit_data.get('nutritions', {})
        st.markdown(f"""
             **Calories**: {nutrients.get('calories', 'N/A')}  
             **Sugar**: {nutrients.get('sugar', 'N/A')}g  
             **Carbs**: {nutrients.get('carbohydrates', 'N/A')}g  
             **Protein**: {nutrients.get('protein', 'N/A')}g  
             **Fat**: {nutrients.get('fat', 'N/A')}g  
             """)

    # st.write(ingredients_string)


    # my_insert_stmt = """ insert into smoothies.public.orders (ingredients, name_on_order)
    #        values ('""" + ingredients_string + """', '""" + name_on_order + """')"""
    # st.write(my_insert_stmt)

    # time_to_insert = st.button('Submit Order')
    if time_to_insert:
        session.sql("""INSERT INTO smoothies.public.orders (ingredients, name_on_order) VALUES ('Cantaloupe', 'DirectInsert')""").collect()
#        session.sql(f"""INSERT INTO smoothies.public.orders (ingredients, name_on_order)VALUES ('{ingredients_string.strip()}', '{name_on_order}')""").collect()
        st.success('Your Smoothie is ordered, '+name_on_order+'!', icon='✅')


