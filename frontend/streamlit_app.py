import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
from api_utils import fetch_jobs_data, send_message
import os

JOBS_ENDPOINT = os.getenv("JOBS_ENDPOINT")
MESSAGE_ENDPOINT = os.getenv("MESSAGE_ENDPOINT")

def init_page():
    st.set_page_config(layout="wide")
    st.title("Jobs and Technologies Table")
    st.write("Select a job and click Start Interview button.")

def update_chat(job_id, user_msg):
    if user_msg:
        st.session_state.messages.append({"role": "user", "content": user_msg})
    response = send_message(MESSAGE_ENDPOINT, job_id, user_msg)
    ai_messages = response["ai_messages"]
    for ai_message in ai_messages:
        st.session_state.messages.append({"role": "assistant", "content": ai_message})

def start_interview():
    update_chat(st.session_state.selected_id, "")

def process_jobs_data(jobs_data):
    df = pd.DataFrame(jobs_data)
    df['Technologies'] = df['technologies'].apply(lambda techs: ', '.join([f"{tech['tech']} - {tech['level']}" for tech in techs]))
    df = df.drop(columns=['technologies'])
    return df


def display_jobs_grid(df):
    columns_order = ['job_name', 'company_name', 'Technologies', 'job_location', 'salary', 'type_of_work', 
                     'experience', 'employment_type', 'operating_mode', 'job_description', 
                     'job_url']
    df_display = df[columns_order]

    df_display.columns = ['Job Name', 'Company', 'Technologies', 'Location', 'Salary', 'Type of Work', 
                  'Experience', 'Employment Type', 'Operating Mode', 'Job Description', 
                  'Job URL']

    gb = GridOptionsBuilder.from_dataframe(df_display)
    gb.configure_selection('single', use_checkbox=True, groupSelectsChildren=False)
    gb.configure_column("Job Name", checkboxSelection=True)
    gridOptions = gb.build()

    grid_response = AgGrid(
        df_display,
        gridOptions=gridOptions,
        data_return_mode='AS_INPUT', 
        update_mode='MODEL_CHANGED', 
        fit_columns_on_grid_load=False,
        theme='streamlit',
        enable_enterprise_modules=False,
        height=400,
        width='100%',
        reload_data=False
    )

    selected = grid_response['selected_rows']

    if selected is not None and not selected.empty:
        selected_row = selected.iloc[0]
        target_job_name = selected_row['Job Name']
        matching_rows = df['job_name'] == target_job_name
        selected_index = df.index[matching_rows].tolist()[0]
        st.session_state.selected_id = int(df.loc[selected_index, 'id'])
        
        # st.write(f"Selected Job ID: {st.session_state.selected_id}")
        # st.write(f"Selected Job Name: {selected_row['Job Name']}")

    st.write("You selected:", selected)
    st.button("Start Interview", type="primary", disabled=selected.empty if selected is not None else True, on_click=start_interview)

def display_chat_interface():
    if "messages" not in st.session_state:
        st.session_state.messages = []

    job_selected = 'selected_id' in st.session_state

    user_message = st.chat_input("Answer the question", disabled=not job_selected)

    if user_message:
        print("#############", st.session_state.selected_id, user_message)
        update_chat(st.session_state.selected_id, user_message)

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

def main():
    init_page()

    jobs_data = fetch_jobs_data(JOBS_ENDPOINT)
    if jobs_data:
        df = process_jobs_data(jobs_data)
        display_jobs_grid(df)
    else:
        st.error(f"Failed to fetch data from the API.")
        st.write("Response content:", jobs_data)

    display_chat_interface()

if __name__ == "__main__":
    main()


# streamlit run streamlit_app.py 