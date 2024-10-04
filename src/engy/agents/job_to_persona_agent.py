import random
from typing import Callable

from ..llm import query_llm

SYSTEM_PROMPT = '''**Role:** You are a persona creation specialist.

**Goal:** Create a detailed persona based on the provided job description.

**Process:**
1. Analyze the job description to extract key skills, responsibilities, and requirements.
2. Create a fictional persona that would be an ideal candidate for this job.
3. Output the generated persona in a <PERSONA></PERSONA> block.

The persona should include:
- Name
- Age
- Living Location
- Grow-up Location
- Background (education and work experience)
- Key skills and strengths
- Personality traits
- Career goals
- A brief personal story related to their professional journey
'''

def parse_persona(text):
    """
    Parses a string containing a `<PERSONA>` block and returns it as a dictionary.

    Args:
        text: The input string containing the persona.

    Returns:
        A dictionary representing the persona.
    """
    start_tag = "<PERSONA>"
    end_tag = "</PERSONA>"
    start_index = text.find(start_tag)
    end_index = text.find(end_tag)
    
    if start_index == -1 or end_index == -1:
        raise ValueError("Missing PERSONA tags in the response")
    
    persona_text = text[start_index + len(start_tag):end_index].strip()
    
    # Split the persona text into lines and create a dictionary
    persona_dict = {}
    current_key = None
    for line in persona_text.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            current_key = key.strip()
            persona_dict[current_key] = value.strip()
        elif current_key:
            persona_dict[current_key] += ' ' + line.strip()
    
    return persona_dict

def job_description_to_persona_agent(job_description: str, producer: Callable[[dict], None]):
    query = f'''<JOB_DESCRIPTION>
{job_description}
</JOB_DESCRIPTION>

Based on this job description, create a detailed persona for an ideal candidate.
'''
    responses, _ = query_llm(query, system_message=SYSTEM_PROMPT,
                             model="claude-3-sonnet-20240229", temperature=0.7, filename='job_description_to_persona_agent')
    
    persona = parse_persona(responses[0])
    producer(persona)

def _terminal_producer(entity):
    print("Generated Persona:")
    for key, value in entity.items():
        print(f"{key}: {value}")

if __name__ == '__main__':
    job_description = """
    Senior Software Engineer - AI/ML
    
    We are seeking a Senior Software Engineer specializing in AI/ML to join our dynamic team. The ideal candidate will have a strong background in machine learning, deep learning, and software engineering. They will be responsible for designing, implementing, and maintaining AI/ML models and systems.

    Responsibilities:
    - Develop and implement machine learning algorithms and models
    - Collaborate with data scientists and product managers to bring AI solutions to production
    - Optimize existing ML models for performance and scalability
    - Contribute to the design and development of our AI infrastructure

    Requirements:
    - Bachelor's or Master's degree in Computer Science, AI, or related field
    - 5+ years of experience in software engineering with a focus on AI/ML
    - Proficiency in Python and experience with ML frameworks (e.g., TensorFlow, PyTorch)
    - Strong understanding of machine learning concepts and techniques
    - Experience with cloud platforms (AWS, GCP, or Azure) and containerization (Docker, Kubernetes)
    - Excellent problem-solving and communication skills
    """
    
    job_description_to_persona_agent(job_description, _terminal_producer)