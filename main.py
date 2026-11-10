import streamlit as st
import requests as req
import os


PHOTO_PATH = "photo"
ENTRY_PATH = "entries"

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
            
            title = st.text_input("Name of this catch")
            
            fish_type = st.selectbox(options=fishes, placeholder="Type to search...", label="Select the fish you caught. If you don't know, click on 'Unknown'")
            
            submit = st.form_submit_button(label="Submit")
            
        if submit:
            file_name = uploaded_picture.name
            
            new_photo = os.path.join(PHOTO_PATH, file_name)
            
            
            with open(new_photo, "wb") as f:
                f.write(uploaded_picture.getbuffer())
            
            entry = {
                "file_name": uploaded_picture.name,
                "title": title,
                "fish_species": fish_type
            }
            
            print(entry)
            
                
if __name__ == "__main__":
    main()