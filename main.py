import streamlit as st
from streamlit_geolocation import streamlit_geolocation
import requests as req
import pandas as pd
from datetime import datetime
import os, time

PHOTO_PATH = "photo"
ENTRY_PATH = "entries"

API_URL = "https://api.inaturalist.org/v1/taxa"

if not os.path.exists(PHOTO_PATH):
    os.makedirs(PHOTO_PATH)
    
    
if not os.path.exists(ENTRY_PATH):
    os.makedirs(ENTRY_PATH)

ENTRY_CSV = os.path.join(ENTRY_PATH, "entries.csv")

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
    
def transform_to_data_list(data):
    res = {}
    
    for i in range(1, len(data)):
            raw = data[i]
            
            title = raw[1]
            
            entry = {
                'file_name': raw[0],
                'title': raw[1],
                'species': raw[2],
                'lat': raw[4],
                'lot': raw[3],
                'datetime': raw[5]
            }
        
            res[title] = entry
            
    return res

def transform_to_species_frequency_table(data):
    return data['fish_species'].value_counts().rename_axis("species").reset_index(name="frequency")

def transform_to_date_frequency_table(data):
    return data['datetime'].value_counts().rename_axis("date").reset_index(name="frequency")
    
if not os.path.exists(PHOTO_PATH):
    os.makedirs(PHOTO_PATH)

if not os.path.exists(ENTRY_PATH):
    os.makedir(ENTRY_PATH)



def main():
    st.title('Fish Track')
    st.header('A way to keep track of fish')
    
    home, upload, history, visualization, record = st.tabs(["Home", "Upload", "History", "Visualization", "Fish Record"])
    
    with home:
        st.text("Welcome to Fish Track\nAn app designed for fishermen to record their best catches.")
        
        
    with upload:
        location = streamlit_geolocation()
        st.caption("Click above to load in your current position")
        
        
        with st.form(key="user-form"):
            uploaded_picture = st.file_uploader("Upload the picture of your catch! (jpg, png)", type=["jpg", "png"])
            
            title = st.text_input("What do you want to name this entry?")
            
            fish_type = st.text_input("What species is this? Avoid nicknames; please use common name or scientific name")
            
            latitude = st.number_input(label="Latitude of location", value=location['latitude'])
            
            longitude = st.number_input(label="Longitude of location", value=location['longitude'])
            
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
    with visualization:
        raw = load_from_csv(ENTRY_CSV)
        
        data = raw.to_numpy()
        
        map_data = raw.to_dict()
        
        db = transform_to_data_list(data)
        
        st.title("Statistics")
        
        st.header("Table")
        
        st.dataframe(raw)

        st.header("Map of Catches")
        st.map(map_data, color="#ADD8E6")
        
        # Count
        st.header("Frequency of Species")
        st.bar_chart(transform_to_species_frequency_table(raw), x="species", y="frequency", x_label="Species", y_label="Count")
        
        st.header("Number of Catches a Day")
        st.line_chart(transform_to_date_frequency_table(raw), x="date", y="frequency")
        
    with history:
        data = load_from_csv(ENTRY_CSV).to_numpy()
        
        db = transform_to_data_list(data)
        
        titles = db.keys()
        
        query = st.text_input("Search for titles of your best catches", placeholder="Type in to search - Press enter to search")
        
        if query:
            results = [title for title in titles if query in title]
        else:
            results = titles
            
        with st.container(height=200):
            chosen_entry = st.radio("Select a entry to view more", options=results)
            
        if chosen_entry:
            entry_data = db[chosen_entry]
            
            st.title(entry_data['title'])
            
            st.header(f"Species: {entry_data['species']}")
            
            
            try:
                st.image(image=PHOTO_PATH + "/" + entry_data['file_name'])
            except Exception:
                st.error("Could not find image. It has either been deleted or moved")
                
            st.text(f"Coordinates caught ({entry_data['lat']},{entry_data['lot']})")
            
            st.text(f"Date & time captured: {entry_data['datetime']}")
                
            
            
            # st.image(PHOTO_PATH.join(entry_data['file_name']))

    with record:
        data = load_from_csv(ENTRY_CSV)

        raw = set(data['fish_species'])
        
        query = st.text_input("Search common names", placeholder="Type in to search - Press enter to search")
        
        if query:
            fish_names = [fish for fish in raw if query in fish]
        else:
            fish_names = raw

        with st.container(height=200):
            chosen_fish = st.radio(label="Select species to examine", options=fish_names, index=None)

        if chosen_fish:
            params = {
                'q': chosen_fish
            }
            
            request = req.get(API_URL, params=params).json()
            
            res = request['results']
            
            if len(res) == 0:
                st.info("Sorry, we couldn't find any information regarding this species")
                
            fish = res[0]
            
            id = fish['id']
            
            time.sleep(1)
            
            summary = req.get(API_URL + "/" + str(id)).json()['results'][0]
            
            
            photo = fish['default_photo']
            
            st.title(f"Scientific name: {fish['name']}")
                        
            st.header(f"Common name: {fish['preferred_common_name']}")
            
            st.image(photo['medium_url'], output_format="JPEG", width=400)
            st.caption(photo['attribution'])

            if summary and "wikipedia_summary" in summary:
                st.html(summary['wikipedia_summary'])
            else:
                st.text("No summary provided. Check the wikipedia link below for more information")
            
            st.text(f"Wikipedia link: {fish['wikipedia_url']}")
            
            
                
if __name__ == "__main__":
    main()