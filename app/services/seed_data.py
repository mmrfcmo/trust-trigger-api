"""Seed default prompt templates and trust framework into the database."""
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.prompt_library import PromptTemplate, PromptCategory
from app.models.trust_framework import TrustFramework, TrustCategory, TrustStandardDef, StandardRecommendation


DEFAULT_SYSTEM_PROMPT = """You are an expert AI visibility consultant. You help local businesses 
improve their trust signals so they appear in AI search results (ChatGPT, Google AI, Perplexity, etc.).
You write in clear, professional British English. Be specific, actionable, and data-driven."""

DEFAULT_PROMPTS = {
    PromptCategory.trust_snapshot: {
        "name": "Trust Snapshot",
        "description": "One-page executive summary with score, strengths, gaps, and next step",
        "user_prompt": """Create a one-page Trust Snapshot for this business.
Format as a professional report section with:
- Executive Summary (2-3 sentences)
- Current Trust Score and Grade
- Key Strengths (top 3)
- Key Gaps (top 3)
- Recommended Next Step
Use markdown formatting. Be concise and actionable.""",
    },
    PromptCategory.transformation_report: {
        "name": "Transformation Report",
        "description": "Full trust transformation report with timeline",
        "user_prompt": """Create a detailed Trust Transformation Report.
Include:
1. Executive Summary
2. Current State Assessment
3. Trust Score Breakdown by Pillar
4. Recommended Improvements (prioritised)
5. Implementation Timeline (4-week plan)
6. Expected Impact
Use markdown with headings and bullet points. Be thorough and specific.""",
    },
    PromptCategory.homepage_rewrite: {
        "name": "Homepage Rewrite",
        "description": "AI-optimised homepage copy under 300 words",
        "user_prompt": """Rewrite the homepage content for this business.
The homepage should:
- Clearly state what the business does in the first sentence
- Build trust immediately
- Include a clear call-to-action
- Be AI-friendly (clear structure, semantic HTML guidance)
- Be under 300 words
Output the rewritten homepage copy in markdown.""",
    },
    PromptCategory.review_request_email: {
        "name": "Review Request Email",
        "description": "Professional email template asking for Google reviews",
        "user_prompt": """Write a professional email template asking customers to leave a Google Review.
The email should:
- Be polite and appreciative
- Include a direct link to Google review page
- Be under 200 words
- Include subject line
Output the full email template.""",
    },
    PromptCategory.trust_journey_summary: {
        "name": "Trust Journey Summary",
        "description": "Summarise a client's trust improvement journey",
        "user_prompt": """Create a Trust Journey Summary for this client.
Include:
1. Starting point (baseline score and grade)
2. Key improvements made
3. Current score and grade
4. Timeline of progress
5. Before/After comparison
6. Certificate of achievement
Make it celebratory and persuasive. Use markdown.""",
    },
}


async def seed_default_prompts(db: AsyncSession):
    """Seed default prompts if none exist."""
    from sqlalchemy import select, func

    result = await db.execute(select(func.count()).select_from(PromptTemplate))
    count = result.scalar() or 0
    if count > 0:
        return  # Already seeded

    for category, config in DEFAULT_PROMPTS.items():
        prompt = PromptTemplate(
            organisation_id=None,  # Global prompt
            category=category,
            name=config["name"],
            description=config["description"],
            version=1,
            is_active=True,
            system_prompt=DEFAULT_SYSTEM_PROMPT,
            user_prompt_template=config["user_prompt"],
            temperature=0.7,
            max_tokens=2000,
            model="gpt-4o-mini",
            variables=["business_name", "website", "trust_score", "grade", "pillars", "improvements"],
        )
        db.add(prompt)

    await db.flush()


async def seed_default_framework(db: AsyncSession):
    """Seed the default trust framework if none exists."""
    from sqlalchemy import select, func

    result = await db.execute(select(func.count()).select_from(TrustFramework))
    count = result.scalar() or 0
    if count > 0:
        return

    framework = TrustFramework(
        organisation_id=None,
        name="Trust Trigger Standard Framework",
        description="Default trust scoring framework with 5 pillars and 14 standards",
        version=1,
        is_active=True,
    )
    db.add(framework)
    await db.flush()

    # Categories
    categories = {
        "online_presence": TrustCategory(framework_id=framework.id, name="Online Presence", slug="online-presence",
            description="Digital footprint and discoverability", max_score=25, sort_order=1),
        "reputation": TrustCategory(framework_id=framework.id, name="Reputation", slug="reputation",
            description="Social proof and credibility signals", max_score=30, sort_order=2),
        "engagement": TrustCategory(framework_id=framework.id, name="Engagement", slug="engagement",
            description="Customer interaction and conversion readiness", max_score=20, sort_order=3),
        "transparency": TrustCategory(framework_id=framework.id, name="Transparency", slug="transparency",
            description="Openness and information accessibility", max_score=15, sort_order=4),
        "technical": TrustCategory(framework_id=framework.id, name="Technical Health", slug="technical",
            description="Website technical quality and security", max_score=10, sort_order=5),
    }
    for cat in categories.values():
        db.add(cat)
    await db.flush()

    # Standards with detection patterns and recommendations
    standards_data = [
        # Online Presence
        (categories["online_presence"], "HTTPS Enabled", "https", 10, "http_header",
         r"detect_https", [
             ("Enable HTTPS", "Install an SSL certificate to secure your website. Visitors and AI trust HTTPS sites more.", "medium", "5-10 points"),
         ]),
        (categories["online_presence"], "Business Categories", "categories", 10, "api_call",
         r"google_categories", [
             ("Set Business Categories", "Select relevant categories on your Google Business profile so AI can classify you correctly.", "low", "5 points"),
         ]),
        (categories["online_presence"], "Business Description", "description", 5, "api_call",
         r"google_description", [
             ("Complete Business Description", "Write a detailed, keyword-rich description of your business on Google.", "low", "5 points"),
         ]),
        # Reputation
        (categories["reputation"], "Google Rating", "rating", 15, "api_call",
         r"rating >= 4.0", [
             ("Improve Google Rating", "Encourage satisfied customers to leave positive Google reviews to boost your rating above 4.0.", "medium", "10-15 points"),
         ]),
        (categories["reputation"], "Google Reviews", "reviews", 10, "api_call",
         r"reviews_count", [
             ("Increase Review Volume", "Ask customers to leave reviews on Google. More reviews build credibility with AI and users.", "low", "5-10 points"),
         ]),
        (categories["reputation"], "Testimonials on Website", "testimonials", 5, "regex",
         r"testimonial|review|what our clients say", [
             ("Collect and Display Reviews", "Add a testimonials section and link to your Google Reviews or Trustpilot profile.", "medium", "5 points"),
         ]),
        # Engagement
        (categories["engagement"], "Call-to-Action", "cta", 5, "regex",
         r"get started|book now|sign up|call now", [
             ("Add Clear Calls-to-Action", "Include visible CTAs like 'Book Now', 'Get a Quote', or 'Contact Us' on key pages.", "low", "5 points"),
         ]),
        (categories["engagement"], "Contact Page", "contact_page", 5, "regex",
         r"contact|get in touch|reach us", [
             ("Add a Contact Page", "Create a dedicated contact page with phone, email, address, and a contact form.", "low", "5 points"),
         ]),
        (categories["engagement"], "Service Pages", "service_pages", 5, "regex",
         r"service|product|what we do", [
             ("Detail Your Services", "Create dedicated pages for each service or product you offer.", "medium", "5 points"),
         ]),
        (categories["engagement"], "Google Photos", "photos", 5, "api_call",
         r"photos_count", [
             ("Add Photos to Google Profile", "Upload photos of your business, team, and work to your Google Business profile.", "low", "5 points"),
         ]),
        # Transparency
        (categories["transparency"], "About Page", "about_page", 5, "regex",
         r"about us|about|our story", [
             ("Add an About Page", "Tell your story, introduce your team, and explain what makes your business unique.", "low", "5 points"),
         ]),
        (categories["transparency"], "FAQ Section", "faq", 5, "regex",
         r"faq|frequently asked|common questions", [
             ("Add an FAQ Section", "Answer common customer questions to build trust and improve AI understanding.", "low", "5 points"),
         ]),
        (categories["transparency"], "Privacy Policy", "privacy_policy", 5, "regex",
         r"privacy policy|privacy|cookie|gdpr", [
             ("Add a Privacy Policy", "Include a privacy policy page covering data handling and GDPR compliance.", "low", "5 points"),
         ]),
        # Technical
        (categories["technical"], "Mobile Responsive", "mobile_responsive", 10, "meta_tag",
         r"viewport", [
             ("Make Site Mobile-Responsive", "Ensure your website works well on mobile devices with a responsive design.", "medium", "10 points"),
         ]),
    ]

    for cat, name, slug, max_pts, det_type, pattern, recs in standards_data:
        std = TrustStandardDef(
            category_id=cat.id,
            name=name,
            slug=slug,
            max_points=max_pts,
            detection_type=det_type,
            detection_pattern=pattern,
            weight=1.0,
            sort_order=0,
        )
        db.add(std)
        await db.flush()

        for action, detail, effort, impact in recs:
            rec = StandardRecommendation(
                standard_id=std.id,
                action=action,
                detail=detail,
                effort=effort,
                impact=impact,
                ai_prompt_reference=f"improvement_{slug}",
            )
            db.add(rec)

    await db.flush()