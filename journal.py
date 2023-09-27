import streamlit as st
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
import streamlit_authenticator as stauth
import whisper
from pydub import AudioSegment
import os
from audio_recorder_streamlit import audio_recorder

TEXT_HEIGHT = 300

# change logo to a book
st.set_page_config(
    page_title="Personal Journal",
    page_icon="📖"
)

audio_tags = {'comments': 'Converted using pydub!'}

upload_path = "uploads/"
download_path = "downloads/"
uploaded_file = "audiofile.wav"

try:
    os.mkdir(upload_path)
except:
    pass
try:
    os.mkdir(download_path)
except:
    pass

@st.cache_data(persist="disk")
def to_mp3(audio_file, output_audio_file, upload_path, download_path):
    ## Converting Different Audio Formats To MP3 ##
    if audio_file.name.split('.')[-1].lower()=="wav":
        audio_data = AudioSegment.from_wav(os.path.join(upload_path,audio_file.name))
        audio_data.export(os.path.join(download_path,output_audio_file), format="mp3", tags=audio_tags)

    elif audio_file.name.split('.')[-1].lower()=="mp3":
        audio_data = AudioSegment.from_mp3(os.path.join(upload_path,audio_file.name))
        audio_data.export(os.path.join(download_path,output_audio_file), format="mp3", tags=audio_tags)

    elif audio_file.name.split('.')[-1].lower()=="ogg":
        audio_data = AudioSegment.from_ogg(os.path.join(upload_path,audio_file.name))
        audio_data.export(os.path.join(download_path,output_audio_file), format="mp3", tags=audio_tags)

    elif audio_file.name.split('.')[-1].lower()=="wma":
        audio_data = AudioSegment.from_file(os.path.join(upload_path,audio_file.name),"wma")
        audio_data.export(os.path.join(download_path,output_audio_file), format="mp3", tags=audio_tags)

    elif audio_file.name.split('.')[-1].lower()=="aac":
        audio_data = AudioSegment.from_file(os.path.join(upload_path,audio_file.name),"aac")
        audio_data.export(os.path.join(download_path,output_audio_file), format="mp3", tags=audio_tags)

    elif audio_file.name.split('.')[-1].lower()=="flac":
        audio_data = AudioSegment.from_file(os.path.join(upload_path,audio_file.name),"flac")
        audio_data.export(os.path.join(download_path,output_audio_file), format="mp3", tags=audio_tags)

    elif audio_file.name.split('.')[-1].lower()=="flv":
        audio_data = AudioSegment.from_flv(os.path.join(upload_path,audio_file.name))
        audio_data.export(os.path.join(download_path,output_audio_file), format="mp3", tags=audio_tags)

    elif audio_file.name.split('.')[-1].lower()=="mp4":
        audio_data = AudioSegment.from_file(os.path.join(upload_path,audio_file.name),"mp4")
        audio_data.export(os.path.join(download_path,output_audio_file), format="mp3", tags=audio_tags)
    return output_audio_file

@st.cache_resource()
def process_audio(filename):
    model = whisper.load_model("base")
    result = model.transcribe(filename)
    return result["text"]

def reset_modifying():
    st.session_state["modifying"] = False

authenticator = stauth.Authenticate(
    dict(st.secrets['credentials']).copy(),
    st.secrets['cookie']['name'],
    st.secrets['cookie']['key'],
    st.secrets['cookie']['expiry_days']
    )

name, authentication_status, username = authenticator.login('Login', 'main')
# print(name, authentication_status, username)

if authentication_status:
    authenticator.logout('Logout', 'sidebar')

    # Initialize connection.
    @st.cache_resource
    def init_connection():
        uri = st.secrets["mongo"].uri
        return MongoClient(uri, server_api=ServerApi('1'))

    client = init_connection()

    # Pull data from the collection.
    # Uses st.cache_data to only rerun when the query changes or after 10 min.
    @st.cache_data(ttl=600)
    def get_data(num_entries, start_date, end_date):
        start_date = datetime.combine(start_date, datetime.max.time())
        end_date = datetime.combine(end_date, datetime.min.time())
        try:
            items = client.journal_entries.entries.find(
                {"date": {"$gte": end_date, "$lte": start_date}},
                limit=num_entries,
            )
            items = list(items)

        except Exception as e:
            st.warning("Failed to load from MongoDB collection.")
            st.error(repr(e))
            items = []
        return items

    if not st.session_state.get("modifying", False):
        # Add a new entry.
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("New Entry")
        # audio upload
        with col2:
            audio_bytes = audio_recorder(
                text="",
                icon_size="3x",
            )
        if audio_bytes is not None:
            with open(os.path.join(upload_path, uploaded_file.name),"wb") as f:
                f.write((uploaded_file).getbuffer())
            with st.spinner(f"Processing Audio ... 💫"):
                output_audio_file = uploaded_file.name.split('.')[0] + '.mp3'
                output_audio_file = to_mp3(uploaded_file, output_audio_file, upload_path, download_path)
                audio_file = open(os.path.join(download_path,output_audio_file), 'rb')
                audio_bytes = audio_file.read()
            with st.spinner(f"Generating Transcript... 💫"):
                transcript = process_audio(str(os.path.abspath(os.path.join(download_path, output_audio_file))))
        else:
            transcript = None
        entry = st.text_area(label="Entry", height=TEXT_HEIGHT, label_visibility="hidden", value=transcript)
        submit = st.button("Add entry", use_container_width=True)

        st.divider()
        
        if submit and entry:
            date = datetime.now()
            client.journal_entries.entries.insert_one({"date": date, "entry": entry})
            get_data.clear()
            st.experimental_rerun()

        # sidebar to filter by date
        st.sidebar.subheader("Filter by date")
        today = datetime.now()
        start_date = st.sidebar.date_input("Start date", today)
        one_year_ago = today.replace(year=today.year - 1)
        end_date = st.sidebar.date_input("End date", one_year_ago)

        # number of entries
        st.sidebar.subheader("Number of entries")
        num_entries = st.sidebar.slider(
            "Select number of entries", 1, 10, 3
        )


        # Show previous 5 previous entries.
        st.subheader("Previous Entries")
        items = get_data(num_entries, start_date, end_date)
        for item in items:
            date = item["date"].strftime("%b %d, %Y")
            st.markdown(f"**{date} -**  {item['entry']}")
            modify = st.button("Modify", key="modify_"+repr(item["_id"]),
                                use_container_width=True)
            # option to modify
            if modify:
                st.session_state["modifying"] = True
                st.session_state["entry"] = item["entry"]
                st.session_state["date"] = item["date"]
                st.session_state["id"] = item["_id"]
                st.experimental_rerun()

    else:
        # Modify an existing entry.
        header_columns = st.columns(3)

        header_columns[0].subheader("Modify Entry")
        header_columns[2].button("Return", key="come_back", use_container_width=True,
                                on_click = reset_modifying)
        id = st.session_state["id"]
        date = st.session_state["date"]
        entry = st.text_area("Entry", st.session_state["entry"], height=TEXT_HEIGHT,
                            label_visibility="hidden")

        col1, col2 = st.columns(2)

        delete = col1.button("Delete entry", use_container_width=True)
        if delete:
            client.journal_entries.entries.delete_one(
                {"_id": id},
            )
            st.session_state["modifying"] = False
            get_data.clear()
            st.experimental_rerun()

        submit = col2.button("Modify entry", use_container_width=True)
        if submit:
            client.journal_entries.entries.update_one(
                {"_id": id},
                {"$set": {"entry": entry}},
            )
            st.session_state["modifying"] = False
            get_data.clear()
            st.experimental_rerun()

elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')