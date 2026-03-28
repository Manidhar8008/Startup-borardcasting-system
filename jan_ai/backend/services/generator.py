import os
import openai

def generate_post(topic: str, tone: str, platform: str, profile: dict = None) -> str:
    """Uses OpenAI to generate a social media post."""
    api_key = os.getenv("OPENAI_API_KEY")
    
    profile_context = ""
    if profile:
        profile_context = f"Context -> Business: {profile.get('business_type', 'General')}. Audience: {profile.get('audience', 'Everyone')}."

    if not api_key:
        # Fallback mock post if no API key is provided for strict MVP execution
        return f"{profile_context}\n[Generated {tone} post for {platform} about {topic}]\nExcited to share our brand new insights on {topic}!"
        
    client = openai.OpenAI(api_key=api_key)
    prompt = f"Write a {tone} social media post for {platform} about {topic}. {profile_context}"
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=250
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating content: {str(e)}"
