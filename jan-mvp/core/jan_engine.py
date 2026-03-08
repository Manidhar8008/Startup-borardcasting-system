"""
JAN Engine Core

Main orchestration engine that runs the AI pipeline.
"""
from agents.strategy_agent import generate_strategy
from agents.content_agent import generate_content
from memory.business_profile import load_business_profile

def run_pipeline(idea: str) -> str:
    """
    Executes the full social media automation pipeline for a given idea.
    
    Steps:
    1. Loads the business profile.
    2. Generates a strategic marketing plan based on the profile and idea.
    3. Generates social media content based on the strategy.
    
    Args:
        idea: The initial seed idea from the user.
        
    Returns:
        A formatted string containing the generated strategy and content.
    """
    print(f"Starting pipeline for idea: '{idea}'")
    
    # Step 1: Load the business profile
    # Using a default brand_id for the MVP
    business_profile = load_business_profile("default_brand")
    print("Business profile loaded.")

    # Step 2: Generate strategy
    print("Generating strategy...")
    strategy = generate_strategy(idea, business_profile)

    # Step 3: Generate content
    print("Generating content...")
    content = generate_content(strategy, business_profile)

    # Step 4: Return the structured results
    result = f"""
===== STRATEGY =====

{strategy}

===== CONTENT =====

{content}
"""

    print("Pipeline completed successfully.")
    return result
