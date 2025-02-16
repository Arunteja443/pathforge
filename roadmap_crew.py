from crewai import Agent, Task, Crew, Process
from textwrap import dedent
import json
from typing import Dict, List, Optional

class RoadmapCrew:
    def __init__(self, openai_api_key: str):
        self.openai_api_key = openai_api_key
        
    def create_agents(self):
        # Form Designer Agent
        self.form_designer = Agent(
            role='Form Design Specialist',
            goal='Create comprehensive and user-friendly onboarding questionnaires',
            backstory=dedent("""
                You are an expert in designing intuitive and effective questionnaires.
                You understand how to gather relevant information while keeping forms
                concise and user-friendly.
            """),
            verbose=True,
            allow_delegation=False
        )
        
        # Research Specialist Agent
        self.researcher = Agent(
            role='Research Specialist',
            goal='Analyze learning paths and gather comprehensive information',
            backstory=dedent("""
                You are an expert in analyzing learning requirements and creating
                structured learning paths. You understand various learning domains
                and can identify key components for success.
            """),
            verbose=True,
            allow_delegation=False
        )
        
        # Resource Curator Agent
        self.curator = Agent(
            role='Resource Curator',
            goal='Curate high-quality learning resources and materials',
            backstory=dedent("""
                You are an expert in finding and organizing educational resources.
                You know how to match resources to different learning styles and
                skill levels.
            """),
            verbose=True,
            allow_delegation=False
        )
        
        # Roadmap Designer Agent
        self.roadmap_designer = Agent(
            role='Roadmap Designer',
            goal='Create personalized learning journeys with clear milestones',
            backstory=dedent("""
                You are an expert in creating structured learning paths with clear
                progression. You know how to break down complex goals into
                manageable steps.
            """),
            verbose=True,
            allow_delegation=False
        )

    def get_onboarding_questions(self, goal_type: str) -> Dict:
        """Generate onboarding questions based on goal type."""
        
        question_generation_task = Task(
            description=dedent(f"""
                Create a comprehensive set of onboarding questions for a {goal_type} goal.
                
                Include questions about:
                1. Current experience and background
                2. Learning preferences and style
                3. Time availability and constraints
                4. Specific goals and objectives
                5. Resource preferences and limitations
                
                Format the response as a JSON object with fields array where each field has:
                - id: string
                - label: string
                - type: "text" | "number" | "select" | "multiselect"
                - required: boolean
                - category: string
                - options: string[] (for select/multiselect)
                - validation: object (if needed)
                - helpText: string
                - order: number
                
                Ensure questions are relevant to {goal_type} specifically.
            """),
            agent=self.form_designer
        )

        crew = Crew(
            agents=[self.form_designer],
            tasks=[question_generation_task],
            verbose=True,
            process=Process.sequential
        )

        result = crew.kickoff()
        return json.loads(result)

    def generate_roadmap(self, goal_type: str, user_responses: Dict) -> Dict:
        """Generate complete roadmap based on goal type and user responses."""
        
        # Research Task
        research_task = Task(
            description=dedent(f"""
                Analyze the learning requirements for {goal_type} based on user responses:
                {json.dumps(user_responses, indent=2)}
                
                Provide research results as JSON with:
                - required_skills: string[]
                - prerequisites: string[]
                - learning_path_components: string[]
                - industry_standards: string[]
                - common_challenges: object[]
            """),
            agent=self.researcher
        )

        # Resource Curation Task
        resource_task = Task(
            description=dedent("""
                Based on the research results, curate learning resources.
                Include various types of resources like courses, tutorials,
                documentation, and practice exercises.
                
                Format as JSON with categorized resources.
            """),
            agent=self.curator
        )

        # Roadmap Design Task
        roadmap_task = Task(
            description=dedent("""
                Create a comprehensive roadmap using the research and resources.
                Include clear milestones, timelines, and checkpoints.
                
                Format as JSON with nodes (learning modules) and edges (prerequisites).
            """),
            agent=self.roadmap_designer
        )

        crew = Crew(
            agents=[self.researcher, self.curator, self.roadmap_designer],
            tasks=[research_task, resource_task, roadmap_task],
            verbose=True,
            process=Process.sequential
        )

        result = crew.kickoff()
        return json.loads(result)

    def validate_milestone(self, milestone_data: Dict) -> Dict:
        """Generate validation questions for a milestone."""
        
        validation_task = Task(
            description=dedent(f"""
                Create validation questions and tasks for the milestone:
                {json.dumps(milestone_data, indent=2)}
                
                Include:
                1. Knowledge assessment questions
                2. Practical tasks
                3. Project requirements
                4. Skill demonstration criteria
                
                Format as JSON with comprehensive validation criteria.
            """),
            agent=self.roadmap_designer
        )

        crew = Crew(
            agents=[self.roadmap_designer],
            tasks=[validation_task],
            verbose=True,
            process=Process.sequential
        )

        result = crew.kickoff()
        return json.loads(result)

# Usage Example
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Initialize crew
    roadmap_crew = RoadmapCrew(openai_api_key=os.getenv("OPENAI_API_KEY"))
    roadmap_crew.create_agents()
    
    # Test onboarding questions
    questions = roadmap_crew.get_onboarding_questions("python_programming")
    print("\nOnboarding Questions:")
    print(json.dumps(questions, indent=2))
    
    # Test roadmap generation
    user_responses = {
        "experience_level": "beginner",
        "weekly_time": 10,
        "learning_style": ["video", "interactive"],
        "goal": "Build web applications with Python"
    }
    
    roadmap = roadmap_crew.generate_roadmap("python_programming", user_responses)
    print("\nRoadmap:")
    print(json.dumps(roadmap, indent=2))