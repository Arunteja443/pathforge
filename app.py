# app.py
import streamlit as st
import json
import os
from roadmap_generator import RoadmapGenerator

# Initialize OpenAI client
@st.cache_resource
def init_generator():
    return RoadmapGenerator(api_key=st.secrets["OPENAI_API_KEY"])

# Page configuration
st.set_page_config(
    page_title="Learning Roadmap Generator",
    page_icon="🎯",
    layout="wide"
)

# Initialize session state
if 'current_step' not in st.session_state:
    st.session_state.current_step = 'goal_selection'
if 'user_responses' not in st.session_state:
    st.session_state.user_responses = {}
if 'onboarding_questions' not in st.session_state:
    st.session_state.onboarding_questions = None
if 'roadmap' not in st.session_state:
    st.session_state.roadmap = None

# Initialize generator
generator = init_generator()

# Title
st.title("🎯 Learning Roadmap Generator")

# Goal Selection Step
if st.session_state.current_step == 'goal_selection':
    st.header("What would you like to learn?")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        goal_type = st.selectbox(
            "Select your learning goal",
            options=[
                "python_programming",
                "web_development",
                "data_science",
                "machine_learning",
                "business_development",
                "product_management"
            ]
        )
    
    if st.button("Next", type="primary"):
        with st.spinner("Generating questions..."):
            try:
                # Get onboarding questions
                questions = generator.get_onboarding_questions(goal_type)
                st.session_state.onboarding_questions = questions
                st.session_state.user_responses['goal_type'] = goal_type
                st.session_state.current_step = 'onboarding'
                st.rerun()
            except Exception as e:
                st.error(f"Error generating questions: {str(e)}")

# Onboarding Questions Step
elif st.session_state.current_step == 'onboarding':
    st.header("Let's customize your learning journey")
    
    questions = st.session_state.onboarding_questions
    responses = {}
    
    for field in questions['fields']:
        if field['type'] == 'select':
            responses[field['id']] = st.selectbox(
                field['label'],
                options=field['options'],
                help=field.get('helpText', ''),
                key=field['id']
            )
        elif field['type'] == 'multiselect':
            responses[field['id']] = st.multiselect(
                field['label'],
                options=field['options'],
                help=field.get('helpText', ''),
                key=field['id']
            )
        elif field['type'] == 'number':
            responses[field['id']] = st.number_input(
                field['label'],
                min_value=field.get('validation', {}).get('min', 0),
                max_value=field.get('validation', {}).get('max', 100),
                help=field.get('helpText', ''),
                key=field['id']
            )
        else:  # text or textarea
            responses[field['id']] = st.text_input(
                field['label'],
                help=field.get('helpText', ''),
                key=field['id']
            )
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back"):
            st.session_state.current_step = 'goal_selection'
            st.rerun()
    
    with col2:
        if st.button("Generate Roadmap", type="primary"):
            with st.spinner("Generating your personalized roadmap..."):
                try:
                    # Update user responses
                    st.session_state.user_responses.update(responses)
                    
                    # Generate roadmap
                    roadmap = generator.generate_roadmap(
                        st.session_state.user_responses['goal_type'],
                        st.session_state.user_responses
                    )
                    st.session_state.roadmap = roadmap
                    st.session_state.current_step = 'roadmap'
                    st.rerun()
                except Exception as e:
                    st.error(f"Error generating roadmap: {str(e)}")

# Roadmap Display Step
elif st.session_state.current_step == 'roadmap':
    st.header("Your Personalized Learning Roadmap")
    
    roadmap = st.session_state.roadmap
    
    # Display Research Insights
    with st.expander("📚 Research Insights", expanded=True):
        insights = roadmap.get('research_insights', {})
        if insights:
            st.write("**Key Concepts:**")
            for concept in insights.get('key_concepts', []):
                st.write(f"- {concept}")
            
            st.write("\n**Prerequisites:**")
            for prereq in insights.get('prerequisites', []):
                st.write(f"- {prereq}")
            
            st.write(f"\n**Learning Approach:** {insights.get('learning_approach', '')}")
            st.write(f"**Estimated Duration:** {insights.get('estimated_duration', '')}")
    
    # Display Resources
    with st.expander("🔍 Recommended Resources", expanded=True):
        resources = roadmap.get('resources', {})
        
        if 'courses' in resources:
            st.subheader("Courses")
            for course in resources['courses']:
                st.write(f"- [{course['title']}]({course['url']}) - {course['duration']} ({course['platform']})")
        
        if 'tutorials' in resources:
            st.subheader("Tutorials")
            for tutorial in resources['tutorials']:
                st.write(f"- [{tutorial['title']}]({tutorial['url']}) ({tutorial['format']})")
        
        if 'documentation' in resources:
            st.subheader("Documentation")
            for doc in resources['documentation']:
                st.write(f"- [{doc['title']}]({doc['url']}) ({doc['type']})")
    
    # Display Roadmap Milestones
    st.subheader("🎯 Learning Milestones")
    for index, milestone in enumerate(roadmap.get('milestones', []), 1):
        with st.expander(f"📍 Milestone {index}: {milestone['title']}", expanded=False):
            st.write(f"**Description:** {milestone['description']}")
            st.write(f"**Duration:** {milestone['duration']}")
            st.write(f"**Complexity:** {milestone['complexity']}")
            
            if milestone.get('exercises'):
                st.write("\n**Exercises:**")
                for exercise in milestone['exercises']:
                    st.write(f"- **{exercise['title']}**: {exercise['description']}")
            
            if milestone.get('checkpoints'):
                st.write("\n**Checkpoints:**")
                for checkpoint in milestone['checkpoints']:
                    st.checkbox(checkpoint, key=f"check_{index}_{checkpoint}")
    
    # Reset Button
    if st.button("Start Over"):
        st.session_state.current_step = 'goal_selection'
        st.session_state.user_responses = {}
        st.session_state.onboarding_questions = None
        st.session_state.roadmap = None
        st.rerun()

# Footer
st.markdown("---")
st.markdown("Made with ❤️ using OpenAI and Streamlit")