"""AI Content Pipeline - Generates all first-draft deliverables automatically."""
import logging
from datetime import datetime
logger = logging.getLogger("trust_trigger.content_pipeline")

GENERATORS = {}

def register_generator(name):
    def decorator(func):
        GENERATORS[name] = func
        return func
    return decorator

@register_generator("homepage_copy")
async def generate_homepage(task, project, scan_data, score_data):
    content = f"""<h2>Welcome to {project.business_name}</h2>
<p>Trusted by customers in your community. We deliver quality service every time.</p>
<h2>Why Choose {project.business_name}?</h2>
<p>We believe in transparency, quality, and customer satisfaction.</p>
<h2>What Our Customers Say</h2>
<p>Our reviews speak for themselves.</p>
<h2>Ready to Get Started?</h2>
<p>Contact us today for a free consultation.</p>"""
    return {"content": content, "word_count": len(content.split()), "sections": ["hero", "value_proposition", "social_proof", "cta"], "generated": True}

@register_generator("email_sequence")
async def generate_email_sequence(task, project, scan_data, score_data):
    emails = [
        {"subject": f"Thanks for reaching out, {project.business_name}!", "body": "Hi there,\n\nThanks for your interest."},
        {"subject": "Meet the team", "body": "Hi there,\n\nWe wanted to introduce ourselves."},
        {"subject": "What our customers are saying", "body": "Hi there,\n\nHere's what our customers say."},
        {"subject": "Frequently asked questions", "body": "Hi there,\n\nHere are answers to common questions."},
        {"subject": "Ready to get started?", "body": "Hi there,\n\nContact us today."},
    ]
    return {"emails": emails, "count": 5, "generated": True}

@register_generator("google_business_posts")
async def generate_gbp_posts(task, project, scan_data, score_data):
    posts = [f"Welcome to {project.business_name}! We're proud to serve our community.",
             f"Tip: Regular maintenance extends the life of your investment.",
             f"We're proud of our 5-star reviews!",
             f"Behind the scenes at {project.business_name}.",
             f"Ready to experience the {project.business_name} difference?",
             f"Did you know? Our team has years of combined experience.",
             f"Question: What's most important when choosing a service provider?",
             f"Thank you to our amazing customers!",
             f"Seasonal tip: Now is the perfect time to schedule your service.",
             f"New to {project.business_name}? Here's what you need to know."]
    return {"posts": posts, "count": len(posts), "generated": True}

@register_generator("social_media_posts")
async def generate_social_posts(task, project, scan_data, score_data):
    return {"facebook": [f"We're {project.business_name}, passionate about quality service.",
                         f"Customer spotlight: Thank you to our amazing clients!",
                         f"Industry tip: How to choose the right service provider.",
                         f"Behind the scenes at {project.business_name}."],
            "instagram": [f"Morning vibes! #ServiceWithASmile",
                         f"Proud to serve our community. #CustomerFirst",
                         f"Tip Tuesday: Save money with regular maintenance! #Tips",
                         f"Thank you for trusting us! #FiveStarService"],
            "count": 8, "generated": True}

async def run_content_generator(task, project):
    task_type = task.type.value if hasattr(task.type, 'value') else task.type
    if task_type not in GENERATORS:
        return {"error": f"No generator for {task_type}", "generated": False}
    scan_data = {}
    score_data = {"overall_percentage": 0, "grade": "unknown"}
    try:
        output = await GENERATORS[task_type](task, project, scan_data, score_data)
        output["task_type"] = task_type
        output["generated_at"] = datetime.now().isoformat()
        return output
    except Exception as e:
        return {"error": str(e), "generated": False}
