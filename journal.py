import streamlit as st
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime

TEXT_HEIGHT = 300

# change logo to a book
st.set_page_config(
    page_title="Personal Journal",
    page_icon="📖"
)

def reset_modifying():
    st.session_state["modifying"] = False

# Initialize connection.
@st.cache_resource
def init_connection():
    uri = st.secrets["mongo"].uri
    return MongoClient(uri, server_api=ServerApi('1'))

client = init_connection()

try:
    user_name = st.experimental_user["name"]
    st.toast(f"Hello {user_name}! 👋")
except KeyError:
    st.toast("Hello! 👋")

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
    st.subheader("New Entry")
    entry = st.text_area(label="Entry", height=TEXT_HEIGHT, label_visibility="hidden")
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

