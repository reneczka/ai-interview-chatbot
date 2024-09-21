import streamlit as st
import requests
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder

st.title("Jobs and Technologies Table")

response = requests.get("http://localhost:8000/jobs/")

if response.status_code == 200:
    jobs_data = response.json()
    
    df = pd.DataFrame(jobs_data)
    
    df['Technologies'] = df['technologies'].apply(lambda techs: ', '.join([f"{tech['tech']} - {tech['level']}" for tech in techs]))
    
    df = df.drop(columns=['technologies', 'id'])
    columns_order = ['job_name', 'company_name', 'job_location', 'salary', 'type_of_work', 
                     'experience', 'employment_type', 'operating_mode', 'job_description', 
                     'job_url', 'Technologies']
    df = df[columns_order]
    
    df.columns = ['Job Name', 'Company', 'Location', 'Salary', 'Type of Work', 
                  'Experience', 'Employment Type', 'Operating Mode', 'Job Description', 
                  'Job URL', 'Technologies']

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_selection('single', use_checkbox=True, groupSelectsChildren=False, groupSelectsFiltered=False)
    gb.configure_grid_options(domLayout='normal')
    gridOptions = gb.build()

    grid_response = AgGrid(
        df,
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
    
    st.write("Selected:", selected)

    if isinstance(selected, pd.DataFrame):
        if not selected.empty:
            if len(selected) == 1:
                st.write("Selected Job for Interview:")
                selected_job = selected.iloc[0].to_dict()
                st.json(selected_job)
            else:
                st.warning("Please select only one job for the interview.")
        else:
            st.write("No job selected for interview.")
    elif isinstance(selected, list):
        if len(selected) > 0:
            if len(selected) == 1:
                st.write("Selected Job for Interview:")
                selected_job = selected[0]
                st.json(selected_job)
            else:
                st.warning("Please select only one job for the interview.")
        else:
            st.write("No job selected for interview.")
    else:
        st.error("Unexpected type for selected rows. Please check the AgGrid configuration.")
        # st.write("Type of selected:", type(selected))

else:
    st.error(f"Failed to fetch data from the API. Status code: {response.status_code}")
    st.write("Response content:", response.text)

# streamlit run frontend/streamlit_app.py