import streamlit as st
import requests
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder

st.set_page_config(layout="wide")
st.title("Jobs and Technologies Table")
st.write("Select a job and click Start Interview button.")

jobs_endpoint_response = requests.get("http://localhost:8000/jobs/")

def start_interview():
    print(f"Sprawdzam czy dziala klik {selected_id}")

def send_user_answer_to_backend_and_get_ai_response(selected_job_id, user_msg):
    response = requests.post(
                "http://localhost:8000/message/",
                json={"job_id": selected_job_id, "user_message": user_msg}
            )
    return response.json()

if jobs_endpoint_response.status_code == 200:
    jobs_data = jobs_endpoint_response.json()
    
    df_original_with_id = pd.DataFrame(jobs_data)
    
    df_original_with_id['Technologies'] = df_original_with_id['technologies'].apply(lambda techs: ', '.join([f"{tech['tech']} - {tech['level']}" for tech in techs]))
    
    df_original_with_id = df_original_with_id.drop(columns=['technologies'])
    columns_order = ['job_name', 'company_name', 'Technologies', 'job_location', 'salary', 'type_of_work', 
                     'experience', 'employment_type', 'operating_mode', 'job_description', 
                     'job_url']

    df_display = df_original_with_id[columns_order]
    
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
        
        # Find the job name of the selected row
        target_job_name = selected_row['Job Name']

        # Find the index in the original DataFrame where the job name matches
        matching_rows = df_original_with_id['job_name'] == target_job_name
        selected_index = df_original_with_id.index[matching_rows].tolist()[0]

        # Retrieve the unique identifier 'id' using the obtained index
        global selected_id
        selected_id = int(df_original_with_id.loc[selected_index, 'id'])
        
        st.write(f"Selected Job ID: {selected_id}")
        st.write(f"Selected Job Name: {selected_row['Job Name']}")


    st.write("Selected:", selected)
    st.button("Start Interview", type="primary", disabled=selected.empty if selected is not None else True, on_click=start_interview)


else:
    st.error(f"Failed to fetch data from the API. Status code: {jobs_endpoint_response.status_code}")
    st.write("Response content:", jobs_endpoint_response.text)


if "messages" not in st.session_state:
    st.session_state.messages = []

did_user_select_job_id = 'selected_id' in globals()
user_message = st.chat_input("Answer the question", disabled=not did_user_select_job_id)

if user_message:
    st.session_state.messages.append({"role": "user", "content": user_message})
    # ai_message = send_user_answer_to_backend_and_get_ai_response().json()
    response = send_user_answer_to_backend_and_get_ai_response(selected_id, user_message)
    ai_messages = response["ai_messages"]
    for ai_message in ai_messages:
        st.session_state.messages.append({"role": "assistant", "content": ai_message})

for ai_message in st.session_state.messages:
    with st.chat_message(ai_message["role"]):
        st.write(ai_message["content"])

        
st.write(st.session_state.messages)

# streamlit run streamlit_app.py