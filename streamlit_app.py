# Import python packages
import streamlit as st
import os
from snowflake.snowpark.functions import col
import streamlit as st
from cryptography.hazmat.primitives import serialization

# Decode the private key from secrets
pem = st.secrets["connections"]["snowflake"]["private_key_content"]["p8_key"].encode()
pwd = st.secrets["connections"]["snowflake"]["private_key_file_pwd"].encode()

pk = serialization.load_pem_private_key(pem, password=pwd)
pk_bytes = pk.private_bytes(
    serialization.Encoding.DER,
    serialization.PrivateFormat.PKCS8,
    serialization.NoEncryption()
)

# Connect using key-pair auth
conn = st.connection("snowflake", private_key=pk_bytes)
session = conn.session()

st.set_page_config(page_title="Custom Smoothie Order Form")

# Write directly to the app
st.title(f"🥤Customize Your Smoothie! :cup_with_straw:" )
st.write(
  """Choose the fruits you want in your custom Smoothie!
  """
)

name_on_order = st.text_input ("Name on Smoothie:")
NAME_ON_ORDER =''
st.write ('Name on the Smoothie will be: ', name_on_order)

# option = st.selectbox(
#    "How would you like to be contacted?",
#    ("Email", "Home phone", "Mobile phone"),
#)
#st.write("You selected:", option)
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

#st.dataframe(data=my_dataframe, use_container_width=True)

ingredients_list = st.multiselect(
'Choose up to 5 ingredients:',
    my_dataframe,
    max_selections = 5
)

if ingredients_list:
    ingredients_string = ''
    #st.write(ingredients_list)
    #st.text(ingredients_list)

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
    #st.write(ingredients_string)
        
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,NAME_ON_ORDER)
                    values ('""" + ingredients_string + """','""" + name_on_order + """' )"""

                    
#    st.write(my_insert_stmt)
#    st.stop
    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        if ingredients_string:
            session.sql(my_insert_stmt).collect()
            st.success('Your Smoothie is ordered,' + name_on_order + '!' , icon="✅")
