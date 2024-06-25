import pandas as pd 
import streamlit as st 
import altair as alt
import matplotlib.pyplot as plt

st.set_page_config(page_title="Havil Academic Database")
st.header("Y10 Result")
st.subheader("Let's analyse")

file_name = "y10-2.csv"
df = pd.read_csv(file_name)

# Getting a list of unique names from the Name column
unique_names = df['Name'].unique()
unique_subjects = ["English", "Mandarin", "Malay", "Math", "Add Math", "Physics", "Biology", "Chemistry", "ICT", "CS", "Business", "Econs"]

def analyseSubject():
    # Select subject from the list
    selected_subject = st.selectbox("Please select a subject:", unique_subjects)  # Exclude 'Name' column

    # Select term from the list
    selected_term = st.selectbox("Please select a term:", ['T1', 'T2', 'T3'])

    # Determine the column name based on selected subject and term
    column_name = f"{selected_subject}-{selected_term}"

    # Filter out NaN values from the selected column
    filtered_data = df.dropna(subset=[column_name])

    # Analyze grades and pass/fail statistics for the selected subject
    analyze_grades(filtered_data[column_name])

# Function to analyze grades and pass/fail statistics
def analyze_grades(scores):
    # Define grade boundaries and categories
    grade_categories = {
        'A': lambda score: score >= 80,
        'B': lambda score: 70 <= score < 80,
        'C': lambda score: 60 <= score < 70,
        'D': lambda score: 50 <= score < 60,
        'E': lambda score: 40 <= score < 50,
        'Fail': lambda score: score < 40
    }

    # Calculate grades distribution
    grade_counts = {grade: sum(map(condition, scores)) for grade, condition in grade_categories.items()}

    # Calculate pass/fail statistics
    pass_count = sum(map(lambda score: score >= 60, scores))
    fail_count = len(scores) - pass_count

    # Create labels and sizes for the grades distribution pie chart
    grade_labels = list(grade_counts.keys())
    grade_sizes = list(grade_counts.values())

    # Assign colors to grades
    grade_colors = {
        'A': '#2ca02c',  # Green
        'B': '#d9c83b',  # Yellow
        'C': '#fc8d62',  # Light red
        'D': '#e6550d',  # Darker red
        'E': '#a63603',  # Even darker red
        'Fail': '#7f0000'  # Red for Fail
    }

    grade_colors_list = [grade_colors.get(grade, '#FFFFFF') for grade in grade_labels]

    # Create labels and sizes for the pass/fail pie chart
    pass_fail_labels = ['Pass', 'Fail']
    pass_fail_sizes = [pass_count, fail_count]
    pass_fail_colors = ['#2ca02c', '#7f0000']  # Green for Pass, Red for Fail

    # Plotting the pie charts
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

    # Grades distribution pie chart
    wedges1, texts1, autotexts1 = ax1.pie(grade_sizes, labels=grade_labels, colors=grade_colors_list, autopct='%1.1f%%', startangle=90)
    ax1.set_title('Grades Distribution')
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle

    # Set text color to white for grades distribution pie chart
    for text1, autotext1 in zip(texts1, autotexts1):
        text1.set_color('white')
        autotext1.set_color('white')

    # Pass/fail pie chart
    wedges2, texts2, autotexts2 = ax2.pie(pass_fail_sizes, labels=pass_fail_labels, colors=pass_fail_colors, autopct='%1.1f%%', startangle=90)
    ax2.set_title('Pass/Fail Statistics')
    ax2.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle

    # Set text color to white for pass/fail pie chart
    for text2, autotext2 in zip(texts2, autotexts2):
        text2.set_color('white')
        autotext2.set_color('white')

    # Set a transparent background
    fig.patch.set_alpha(0.0)
    ax1.patch.set_alpha(0.0)
    ax2.patch.set_alpha(0.0)

    # Display the pie charts using Streamlit
    st.subheader("Grades Distribution:")
    st.pyplot(fig)

    # Calculate class average
    class_average = scores.mean()

    # Find highest score and corresponding student name
    highest_score = scores.max()
    highest_score_name = df.loc[scores.idxmax(), 'Name']

    # Display statistics
    st.subheader("Statistics:")
    st.write(f"Class Average: {class_average:.2f}")
    st.write(f"Highest Score: {highest_score} (Student: {highest_score_name})")

def analyseStudent():
    # Asking the user to select a name from the dropdown
    selected_name = st.selectbox("Please select a name:", unique_names)
    selected_subject = st.selectbox("Please select a subject:", unique_subjects)

    # Filter the DataFrame based on the selected name
    filtered_df = df[df['Name'] == selected_name]
    subject_columns = [f"{selected_subject}-T1", f"{selected_subject}-T2", f"{selected_subject}-T3"]
    # filtered_subject_df = filtered_df[['Name'] + subject_columns]

    # Check if the selected subject columns exist in the filtered DataFrame
    if all(col in filtered_df.columns for col in subject_columns):
        # Check if all selected subject columns are NaN for the selected student
        if filtered_df[subject_columns].isnull().all().all():
            st.write(f"No data available for {selected_subject} for {selected_name}.")
        else:
            # Extract the relevant data for the line chart
            subject_data = filtered_df[subject_columns].transpose()
            subject_data.columns = ['Score']
            subject_data['Term'] = subject_data.index

            # Ensure the columns are numeric
            numeric_subject_columns = df[subject_columns].apply(pd.to_numeric, errors='coerce')

            # Calculate the average scores for each term
            avg_scores = numeric_subject_columns.mean().values
            avg_data = pd.DataFrame({
                'Score': avg_scores,
                'Term': subject_data['Term'],
                'Type': 'Average'
            })

            # Add the type of score (individual or average) to subject_data
            subject_data['Type'] = 'Individual'

            # Combine the individual scores and average scores
            combined_data = pd.concat([subject_data, avg_data])

            # Create a line chart using Altair
            chart = alt.Chart(combined_data).mark_line(point=True).encode(
                x=alt.X('Term', title='Term'),
                y=alt.Y('Score', title='Score', scale=alt.Scale(domain=[0, 100])),  # Adjust the scale as needed
                color='Type:N',
                tooltip=['Term', 'Score', 'Type']
            ).properties(
                title=f"{selected_name}'s Scores in {selected_subject} with Averages"
            ).configure_axis(
                grid=True
            )

            # Display the chart
            st.altair_chart(chart, use_container_width=True)
    else:
        st.write(f"No data available for {selected_subject} for {selected_name}.")

# Main interface to choose between analyzing a student or a subject
analysis_choice = st.radio("Do you want to analyze a subject or a student?", ('None', 'Student', 'Subject'))

# Call the appropriate function based on user choice
if analysis_choice == 'Student':
    analyseStudent()
elif analysis_choice == 'Subject':
    analyseSubject()
else:
    pass
