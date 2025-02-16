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

# Helper function to safely get nested dictionary values
def safe_get(dictionary, *keys, default=None):
    try:
        value = dictionary
        for key in keys:
            value = value[key]
        return value
    except (KeyError, TypeError, IndexError):
        return default

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
    
    fields = safe_get(questions, 'fields', default=[])
    for field in fields:
        field_id = safe_get(field, 'id')
        if not field_id:
            continue

        field_type = safe_get(field, 'type', default='text')
        field_label = safe_get(field, 'label', default='Question')
        field_help = safe_get(field, 'helpText', default='')
        
        if field_type == 'select':
            options = safe_get(field, 'options', default=[])
            if options:
                responses[field_id] = st.selectbox(
                    field_label,
                    options=options,
                    help=field_help,
                    key=field_id
                )
        elif field_type == 'multiselect':
            options = safe_get(field, 'options', default=[])
            if options:
                responses[field_id] = st.multiselect(
                    field_label,
                    options=options,
                    help=field_help,
                    key=field_id
                )
        elif field_type == 'number':
            validation = safe_get(field, 'validation', default={})
            responses[field_id] = st.number_input(
                field_label,
                min_value=safe_get(validation, 'min', default=0),
                max_value=safe_get(validation, 'max', default=100),
                help=field_help,
                key=field_id
            )
        else:  # text or textarea
            responses[field_id] = st.text_input(
                field_label,
                help=field_help,
                key=field_id
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
        insights = safe_get(roadmap, 'research_insights', default={})
        if insights:
            key_concepts = safe_get(insights, 'key_concepts', default=[])
            if key_concepts:
                st.write("**Key Concepts:**")
                for concept in key_concepts:
                    st.write(f"- {concept}")
            
            prerequisites = safe_get(insights, 'prerequisites', default=[])
            if prerequisites:
                st.write("\n**Prerequisites:**")
                for prereq in prerequisites:
                    st.write(f"- {prereq}")
            
            learning_approach = safe_get(insights, 'learning_approach')
            if learning_approach:
                st.write(f"\n**Learning Approach:** {learning_approach}")
            
            estimated_duration = safe_get(insights, 'estimated_duration')
            if estimated_duration:
                st.write(f"**Estimated Duration:** {estimated_duration}")
    
    # Display Resources
    with st.expander("🔍 Recommended Resources", expanded=True):
        resources = safe_get(roadmap, 'resources', default={})
        
        courses = safe_get(resources, 'courses', default=[])
        if courses:
            st.subheader("Courses")
            for course in courses:
                title = safe_get(course, 'title', default='Course')
                url = safe_get(course, 'url', default='#')
                duration = safe_get(course, 'duration', default='')
                platform = safe_get(course, 'platform', default='')
                st.write(f"- [{title}]({url}) - {duration} ({platform})")
        
        tutorials = safe_get(resources, 'tutorials', default=[])
        if tutorials:
            st.subheader("Tutorials")
            for tutorial in tutorials:
                title = safe_get(tutorial, 'title', default='Tutorial')
                url = safe_get(tutorial, 'url', default='#')
                format_type = safe_get(tutorial, 'format', default='')
                st.write(f"- [{title}]({url}) ({format_type})")
        
        docs = safe_get(resources, 'documentation', default=[])
        if docs:
            st.subheader("Documentation")
            for doc in docs:
                title = safe_get(doc, 'title', default='Documentation')
                url = safe_get(doc, 'url', default='#')
                doc_type = safe_get(doc, 'type', default='')
                st.write(f"- [{title}]({url}) ({doc_type})")
    
    # Display Roadmap Milestones
    st.subheader("🎯 Learning Milestones")
    milestones = safe_get(roadmap, 'milestones', default=[])
    for index, milestone in enumerate(milestones, 1):
        title = safe_get(milestone, 'title', default=f'Milestone {index}')
        with st.expander(f"📍 Milestone {index}: {title}", expanded=False):
            description = safe_get(milestone, 'description', default='No description available')
            st.write(f"**Description:** {description}")
            
            duration = safe_get(milestone, 'duration')
            if duration:
                st.write(f"**Duration:** {duration}")
            
            complexity = safe_get(milestone, 'complexity')
            if complexity:
                st.write(f"**Complexity:** {complexity}")
            
            exercises = safe_get(milestone, 'exercises', default=[])
            if exercises:
                st.write("\n**Exercises:**")
                for exercise in exercises:
                    ex_title = safe_get(exercise, 'title', default='Exercise')
                    ex_desc = safe_get(exercise, 'description', default='')
                    st.write(f"- **{ex_title}**: {ex_desc}")
            
            checkpoints = safe_get(milestone, 'checkpoints', default=[])
            if checkpoints:
                st.write("\n**Checkpoints:**")
                for checkpoint in checkpoints:
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