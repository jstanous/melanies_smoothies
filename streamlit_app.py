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

# When Ingredients list is populated with at least 1 item.
if ingredients_list:
    ingredients_string = ''
    time_to_insert = st.button('Submit Order')
    # st.write(ingredients_string)
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
    if time_to_insert:
        # Direct SQL Insert for testing
        # session.sql("""INSERT INTO smoothies.public.orders (ingredients, name_on_order) VALUES ('Cantaloupe', 'DirectInsert')""").collect()
        session.sql(f"""INSERT INTO smoothies.public.orders (ingredients, name_on_order)VALUES ('{ingredients_string.strip()}', '{name_on_order}')""").collect()
        st.success('Your Smoothie is ordered, '+name_on_order+'!', icon='✅')


# When Ingredients list is populated with at least 1 item.
# Display Nutrition Information
if ingredients_list:
    nutrition_data = []
    for fruit_chosen in ingredients_list:
        response = requests.get(f"https://fruityvice.com/api/fruit/{fruit_chosen}")
        fruit_data = response.json()
        nutrients = fruit_data.get('nutritions', {})
        nutrition_data.append({
            "Fruit": fruit_chosen,
            "Calories": nutrients.get('calories', 'N/A'),
            "Sugar (g)": nutrients.get('sugar', 'N/A'),
            "Carbs (g)": nutrients.get('carbohydrates', 'N/A'),
            "Protein (g)": nutrients.get('protein', 'N/A'),
            "Fat (g)": nutrients.get('fat', 'N/A')
            })
    # Convert to DataFrame and display
    nutrition_df = pd.DataFrame(nutrition_data)
    nutrition_df.reset_index(drop=True, inplace=True)
    st.subheader("Nutrition Summary")
    st.dataframe(nutrition_df, use_container_width=True)
