import streamlit as st
import requests as req
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime
import os

load_dotenv()


PHOTO_PATH = "photo"
ENTRY_PATH = "entries"

if not os.path.exists(PHOTO_PATH):
    os.makedirs(PHOTO_PATH)
    
    
ENTRY_CSV = os.path.join(ENTRY_PATH, "entries.csv")
    
    
if not os.path.exists(ENTRY_PATH):
    os.makedirs(ENTRY_PATH)

def save_to_csv(data_dict, csv_file):
    new = pd.DataFrame([data_dict])
    if not os.path.isfile(csv_file):
        new.to_csv(csv_file, mode='w', header=True, index=False)
    else:
        new.to_csv(csv_file, mode='a', header=False, index=False)
        
def load_from_csv(csv_file):
    if os.path.isfile(csv_file):
        return pd.read_csv(csv_file)
    else:
        return pd.DataFrame()


if not os.path.exists(PHOTO_PATH):
    os.makedirs(PHOTO_PATH)

if not os.path.exists(ENTRY_PATH):
    os.makedir(ENTRY_PATH)

# TO-DO; Replace with fish API
fishes = ["Carp", "Salmon", 'Unknown']


def main():
    st.title('Fish Track')
    st.header('A way to keep track of fish')
    
    home, upload, history = st.tabs(["Home", "Upload", "History"])
    
    with home:
        st.text("Welcome to Fish Track\nAn app designed for fishermen to record their best catches.")
        
        st.text("")
        
    with upload:
        
        with st.form(key="user-form"):
            uploaded_picture = st.file_uploader("Upload the picture of your catch! (jpg, png)", type=["jpg", "png"])
            
            title = st.text_input("What do you want to name this entry?")
            
            fish_type = st.text_input("What species is this? Avoid nicknames; please use common name or scientific name")
            
            latitude = st.number_input(label="Latitude of location")
            
            longitude = st.number_input(label="Longitude of location")
            
            dt = st.datetime_input(
                "Select the date and time of when you catch it",
                value=datetime.now(),
                format="MM/DD/YYYY"
            )
            
            confirm = st.checkbox("I assure that the information is accurate and I won't submit the information more than once.")
            
            
            submit = st.form_submit_button(label="Submit")
            
        if submit:
            try:
                if not confirm:
                    raise Exception("Please check the box before submitting")
                
                
                file_name = uploaded_picture.name
                
                new_photo = os.path.join(PHOTO_PATH, file_name)
                
                
                with open(new_photo, "wb") as f:
                    f.write(uploaded_picture.getbuffer())
                
                entry = {
                    "file_name": uploaded_picture.name,
                    "title": title,
                    "fish_species": fish_type,
                    "lon": longitude,
                    "lat": latitude,
                    "datetime": dt.isoformat()
                }
                
                save_to_csv(entry, ENTRY_CSV)
            except Exception as e:
                st.error(f"Failed to save: {e}")
            else:
                st.success("Entry successfully saved!")
            
                
if __name__ == "__main__":
    main()