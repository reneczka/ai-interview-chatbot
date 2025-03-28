import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
from api_utils import fetch_jobs_data, send_message, wake_up_server
import os
from streamlit.components.v1 import html

JOBS_ENDPOINT = os.getenv("JOBS_ENDPOINT")
MESSAGE_ENDPOINT = os.getenv("MESSAGE_ENDPOINT")
BACKEND_URL = os.getenv("BACKEND_URL")

def init_page():
    st.set_page_config(layout="wide")
    st.title("Jobs and Technologies Table")
    st.write("Select a job and click Start Interview button.")

def update_chat(job_id, user_msg):
    if user_msg:
        st.session_state.messages.append({"role": "user", "content": user_msg})
    response = send_message(MESSAGE_ENDPOINT, job_id, user_msg)
    ai_messages = response.get("ai_messages", []) if response else []
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

def wake_up_server_browser():
    """Uses JavaScript in the browser to wake up the Render.com server without displaying anything"""
    
    if "server_wake_attempted" not in st.session_state:
        st.session_state.server_wake_attempted = True
        
        # Create JavaScript to make the wake-up request from the browser silently
        js_code = f"""
        <script>
            // Track start time to enforce maximum wake-up time of 120 seconds
            const startTime = Date.now();
            const MAX_WAKE_TIME = 120000; // 120 seconds
            const RETRY_INTERVAL = 15000; // 15 seconds
            
            // Silent function that just sends requests without UI updates
            async function wakeUpServer(retryCount = 0) {{
                // Check if we've exceeded the maximum time
                const elapsedTime = Date.now() - startTime;
                if (elapsedTime >= MAX_WAKE_TIME) {{
                    console.log('Wake-up time limit reached');
                    return;
                }}
                
                try {{
                    console.log('Attempting to wake up server');
                    
                    // Use a timeout to avoid hanging
                    const controller = new AbortController();
                    const timeoutId = setTimeout(() => controller.abort(), 10000);
                    
                    const response = await fetch('{BACKEND_URL}', {{
                        method: 'GET',
                        headers: {{
                            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                            'Accept': 'text/html,application/xhtml+xml,application/xml',
                            'Accept-Language': 'en-US,en;q=0.9',
                            'Cache-Control': 'no-cache',
                        }},
                        signal: controller.signal,
                    }});
                    
                    clearTimeout(timeoutId);
                    
                    if (response.ok) {{
                        console.log('Server is awake!');
                        // Reload the app to use the now-awake server
                        window.location.reload();
                        return;
                    }} 
                    
                    // For any response, schedule next retry if within time limit
                    if (Date.now() - startTime < MAX_WAKE_TIME - RETRY_INTERVAL) {{
                        setTimeout(() => wakeUpServer(retryCount + 1), RETRY_INTERVAL);
                    }}
                    
                }} catch (error) {{
                    console.error('Error waking up server:', error);
                    
                    // Schedule next retry if within time limit
                    if (Date.now() - startTime < MAX_WAKE_TIME - RETRY_INTERVAL) {{
                        setTimeout(() => wakeUpServer(retryCount + 1), RETRY_INTERVAL);
                    }}
                }}
            }}
            
            // Start the wake-up process immediately
            wakeUpServer();
        </script>
        """
        
        # Directly render the HTML component (no visible elements)
        html(js_code, height=0)
        return True
    
    return False

def main():
    init_page()

    # Wake up the server using browser-based JavaScript (silently)
    wake_up_server_browser()
    
    # Show loading state to the user while backend wakes up
    with st.spinner("Connecting to backend server..."):
        server_ready = wake_up_server()
    
    # Check for jobs data
    jobs_data = fetch_jobs_data(JOBS_ENDPOINT)
    
    # Display single status message based on server and data availability
    if server_ready and jobs_data:
        st.toast("Backend server is ready", icon="✅")
    elif not jobs_data:
        st.warning("Backend server is starting up. Please wait a few moments.", icon="⚠️")
    
    # Only proceed to display grid if we have data
    if jobs_data:
        df = process_jobs_data(jobs_data)
        display_jobs_grid(df)

    display_chat_interface()

if __name__ == "__main__":
    main()


# streamlit run streamlit_app.py 