# roadmap_generator.py
from openai import OpenAI
import json
from typing import Dict, List

class RoadmapGenerator:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def get_onboarding_questions(self, goal_type: str) -> Dict:
        """Generate onboarding questions based on goal type."""
        prompt = f"""
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
        Return only the JSON object, no additional text.
        """

        response = self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You are a form design specialist who creates effective questionnaires."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return json.loads(response.choices[0].message.content)

    def generate_roadmap(self, goal_type: str, user_responses: Dict) -> Dict:
        """Generate complete roadmap based on goal type and user responses."""
        prompt = f"""
        Create a comprehensive learning roadmap for: {goal_type}
        
        User Profile:
        {json.dumps(user_responses, indent=2)}
        
        Create a complete roadmap including:
        1. Research insights about the learning path
        2. Curated resources (courses, tutorials, documentation)
        3. Detailed milestones with:
           - Title and description
           - Duration estimates
           - Complexity level
           - Required exercises
           - Checkpoints for progress tracking
        
        Format the response as a JSON object with:
        - research_insights: object with key findings
        - resources: categorized learning materials
        - nodes: array of learning milestones
        - edges: array of dependencies between milestones
        
        Return only the JSON object, no additional text.
        """

        response = self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You are a learning path expert who creates personalized roadmaps."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return json.loads(response.choices[0].message.content)