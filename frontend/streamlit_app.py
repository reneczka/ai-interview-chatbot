import streamlit as st
import requests
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder

st.set_page_config(layout="wide")
st.title("Jobs and Technologies Table")
st.write("Select a job and click Start Interview button.")

response = requests.get("http://localhost:8000/jobs/")

if response.status_code == 200:
    jobs_data = response.json()
    
    df = pd.DataFrame(jobs_data)
    
    df['Technologies'] = df['technologies'].apply(lambda techs: ', '.join([f"{tech['tech']} - {tech['level']}" for tech in techs]))
    
    df = df.drop(columns=['technologies'])
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
        print(f"# # # # # # # # # # # #{selected_row}")

        selected_index = df[df['job_name'] == selected_row['Job Name']].index[0]
        selected_id = df.loc[selected_index, 'id']
        
        st.write(f"Selected Job ID: {selected_id}")
        st.write(f"Selected Job Name: {selected_row['Job Name']}")

    st.write("Selected:", selected)
    st.button("Start Interview", type="primary", disabled=selected.empty if selected is not None else True)

else:
    st.error(f"Failed to fetch data from the API. Status code: {response.status_code}")
    st.write("Response content:", response.text)


# streamlit run streamlit_app.py