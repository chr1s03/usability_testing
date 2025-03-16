import streamlit as st
import pandas as pd
import time
import os

# Create a folder for data storage
data_folder = "data"
os.makedirs(data_folder, exist_ok=True)

# File paths for CSV data storage
consent_file = os.path.join(data_folder, "consent_data.csv")
demographic_file = os.path.join(data_folder, "demographic_data.csv")
task_file = os.path.join(data_folder, "task_data.csv")
exit_file = os.path.join(data_folder, "exit_data.csv")


def save_to_csv(data_dict, csv_file):
    df_new = pd.DataFrame([data_dict])
    if not os.path.isfile(csv_file):
        df_new.to_csv(csv_file, mode='w', header=True, index=False)
    else:
        df_new.to_csv(csv_file, mode='a', header=False, index=False)


def load_from_csv(csv_file):
    return pd.read_csv(csv_file) if os.path.isfile(csv_file) else pd.DataFrame()


def main():
    st.title("Usability Testing Tool")

    home, consent, demographics, tasks, exit, report = st.tabs([
        "Home", "Consent", "Demographics", "Task", "Exit Questionnaire", "Report"
    ])

    with home:
        st.header("Introduction")
        st.write("""
        Welcome to the Usability Testing Tool.

        This tool allows you to:
        1. Provide consent for participation.
        2. Complete a demographic questionnaire.
        3. Perform usability tasks.
        4. Answer an exit questionnaire.
        5. View aggregated usability data.
        """)

    with consent:
        st.header("Consent Form")
        consent_given = st.checkbox("I agree to participate in this usability study.")
        if st.button("Submit Consent"):
            if consent_given:
                save_to_csv({"timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "consent": "Yes"}, consent_file)
                st.success("Consent recorded.")
            else:
                st.warning("You must agree before proceeding.")

    with demographics:
        st.header("Demographic Questionnaire")
        with st.form("demographic_form"):
            name = st.text_input("Full Name")
            age = st.number_input("Age", min_value=10, max_value=100, step=1, value=None, format="%d")
            occupation = st.text_input("Occupation")
            familiarity = st.radio("Are you familiar with similar tools?", ["Yes", "No", "Somewhat"], index=None)
            submitted = st.form_submit_button("Submit Demographics")
            if submitted:
                save_to_csv({"timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "name": name, "age": age,
                             "occupation": occupation, "familiarity": familiarity}, demographic_file)
                st.success("Demographic data saved.")

    with tasks:
        st.header("Task Page")
        task_name = st.selectbox("Select Task", ["Task 1: Example Task", "Task 2: Navigation Task"])

        if "task_time" not in st.session_state:
            st.session_state["task_time"] = None

        if st.button("Start Task Timer"):
            st.session_state["start_time"] = time.time()
            st.session_state["task_time"] = None  # Reset task time

        if st.button("Stop Task Timer") and "start_time" in st.session_state:
            duration = time.time() - st.session_state["start_time"]
            st.session_state["task_time"] = round(duration, 2)  # Store and display rounded duration

        if st.session_state["task_time"] is not None:
            st.success(f"Final Task Time: {st.session_state['task_time']} seconds")

        success = st.radio("Was the task completed successfully?", ["Yes", "No", "Partial"], index=None)
        notes = st.text_area("Observer Notes")

        if st.button("Save Task Results"):
            duration_val = st.session_state.get("task_time", "N/A")
            save_to_csv({"timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "task": task_name, "success": success,
                         "duration": duration_val, "notes": notes}, task_file)
            st.success("Task data saved.")

    with exit:
        st.header("Exit Questionnaire")
        with st.form("exit_form"):
            satisfaction = st.slider("Overall Satisfaction (1-5)", 1, 5)
            ease_of_use = st.slider("Ease of Use (1-5)", 1, 5)
            design = st.slider("Design Aesthetic (1-5)", 1, 5)
            responsiveness = st.slider("Responsiveness (1-5)", 1, 5)

            feedback_positive = st.text_area("What did you like about the tool?")
            feedback_improvement = st.text_area("What can be improved?")

            submitted_exit = st.form_submit_button("Submit Exit Questionnaire")
            if submitted_exit:
                save_to_csv({
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "satisfaction": satisfaction,
                    "ease_of_use": ease_of_use,
                    "design": design,
                    "responsiveness": responsiveness,
                    "feedback_positive": feedback_positive,
                    "feedback_improvement": feedback_improvement
                }, exit_file)
                st.success("Exit questionnaire data saved.")

    with report:
        st.header("Usability Report")

        # Display all data
        for file, label in [
            (consent_file, "Consent Data"),
            (demographic_file, "Demographic Data"),
            (task_file, "Task Performance Data"),
            (exit_file, "Exit Questionnaire Data")
        ]:
            st.subheader(label)
            df = load_from_csv(file)
            if not df.empty:
                st.dataframe(df)
            else:
                st.info(f"No {label.lower()} available.")

        # Display bar charts
        if not load_from_csv(exit_file).empty:
            exit_df = load_from_csv(exit_file)

            st.subheader("Usability Ratings Breakdown")
            st.bar_chart(exit_df[["satisfaction", "ease_of_use", "design", "responsiveness"]].mean())

            # Display summary statistics
            st.subheader("Summary Statistics")
            st.write(exit_df[["satisfaction", "ease_of_use", "design", "responsiveness"]].describe())

if __name__ == "__main__":
    main()
