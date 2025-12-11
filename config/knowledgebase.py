"""
Inshora Group AI Voice Knowledge Base
Contains domain-specific knowledge for the AI insurance agent.
Last Updated: May 2025
"""

# ===========================
# TEXAS-SPECIFIC INSURANCE LAWS
# ===========================

TEXAS_INSURANCE_LAWS = """
TEXAS-SPECIFIC INSURANCE REGULATIONS:

AUTO INSURANCE:
- State minimums: $30,000 bodily injury per person / $60,000 per accident / $25,000 property damage (30/60/25)
- SR-22: Required for high-risk drivers; Progressive offers SR-22 coverage
- Uninsured/Underinsured motorist coverage is optional but recommended

HOMEOWNERS INSURANCE:
- Windstorm insurance: Required near coastal counties (Galveston, Corpus Christi, etc.)
- Texas Windstorm Insurance Association (TWIA) provides coverage in designated areas
- Standard policies may exclude wind/hail in coastal regions

FLOOD INSURANCE:
- Required in FEMA Zone AE or VE if home has a mortgage
- National Flood Insurance Program (NFIP) policies available
- Private flood insurance options may offer better coverage/rates
"""

# ===========================
# OBJECTION HANDLING SCRIPTS
# ===========================

OBJECTION_HANDLING = """
OBJECTION HANDLING RESPONSES:

"I'm not ready yet."
- "Of course! Would you like me to send you a link where you can complete it at your convenience?"
- "No pressure at all—happy to follow up via text or email when it works better for you."

"I found something cheaper."
- "That makes sense! Just to check—was the quote apples to apples on coverage, or were there differences like liability limits or deductibles?"
- "We often beat other quotes once discounts are applied—mind if I take another look for you?"

"I already have insurance."
- "That's great! Are you looking to compare rates or explore bundling for a discount?"
- "We can usually save people money when they bundle home and auto—want to check?"

"I'm busy, can you call me back?"
- "Of course! I'll send a quick text with a reschedule link. You can choose any time that works for you."

"I want to talk to a human."
- "I totally understand. I'm here to assist you first, and if it still feels better to speak to a person, I'll make that happen right away."
"""

# ===========================
# ESCALATION PROTOCOLS
# ===========================

ESCALATION_PROTOCOLS = """
ESCALATION TRIGGERS & PROTOCOLS:

AUTO-ESCALATE IMMEDIATELY WHEN CLIENT SAYS:
- "lawsuit" or mentions legal action
- "claim denied" or disputes about claims
- "cancel now" or urgent cancellation requests
- CRM lookup fails or system errors occur
- Caller is in distress or mentions injury
- Expresses anger or frustration that cannot be resolved

PRE-TRANSFER DATA REQUIREMENTS:
Before transferring, collect and confirm:
1. Full name
2. Contact number
3. Reason for transfer
4. Product line (auto, home, flood, life, commercial)
5. Policy number (if available)

PREFERRED ESCALATION CHANNELS:
- Transfer live to agent via warm handoff (preferred)
- SMS/email alert to assigned agent with transcript summary
- Schedule callback with licensed agent
"""

# ===========================
# LEAD SCORING MATRIX
# ===========================

LEAD_SCORING = """
LEAD QUALIFICATION & CROSS-SELL OPPORTUNITIES:

| Lead Type                    | Priority  | Cross-Sell | Strategy                          |
|------------------------------|-----------|------------|-----------------------------------|
| Auto only                    | Medium    | Yes        | Suggest home insurance later      |
| Auto + Home                  | High      | Yes        | Push umbrella policy              |
| Life + Annuity               | Very High | No         | Book appointment with specialist  |
| Commercial + Workers Comp    | High      | Yes        | Ask about building coverage       |
| Flood Only                   | Low       | Maybe      | Try home bundling                 |

BUNDLING PRIORITIES:
- Always mention bundling discounts for home + auto
- Life insurance leads should be scheduled for appointments
- Commercial leads need comprehensive coverage review
"""

# ===========================
# TONE & LANGUAGE ADAPTATION
# ===========================

TONE_ADAPTATION = """
CALLER COMMUNICATION STYLE ADAPTATIONS:

IF CALLER IS FAST-TALKING:
- Use short, efficient prompts
- Keep responses brief and to the point
- Example: "Let's confirm a couple quick things to get you rolling."
- Minimize filler words and get straight to questions

IF CALLER IS EMOTIONAL/UPSET:
- Use empathy phrases: "I hear you," "That sounds really frustrating," "Let's work through it together."
- Slow down your pace
- Acknowledge their feelings before problem-solving
- Offer to escalate if needed

IF CALLER IS ELDERLY OR SLOW-PACED:
- Slow down speech significantly
- Confirm often: "Just to double-check, your zip code is 77479, correct?"
- Be patient with repeated questions
- Speak clearly and avoid jargon
- Give them time to respond
"""

# ===========================
# PROMOTIONS & DISCOUNTS
# ===========================

PROMOTIONS_DISCOUNTS = """
CURRENT PROMOTIONS & DISCOUNTS:

ACTIVE CAMPAIGNS:
- May is Life Insurance Awareness Month: $25 Amazon gift card with booked life insurance appointment
- Mention this offer when discussing life insurance

STANDARD DISCOUNTS:
- Bundling Offer: Home + Auto = up to 20% discount
- Multi-policy discount available
- Good driver discount for clean driving records
- Home security system discount
- Loyalty discount for existing customers

REFERRAL PROGRAM:
- $10 gift card per referral that gets quoted
- Encourage satisfied customers to refer friends and family
"""

# ===========================
# REBUTTAL & REDIRECTION SCRIPTS
# ===========================

REBUTTALS = """
ADVANCED REBUTTAL & REDIRECTION SCRIPTS:

WHEN CALLER ASKS FOR DISCOUNT UP FRONT:
- "Absolutely—we'll look for all available discounts after I gather a few details. Let's start with your zip code."

REBUTTAL TO "You're just a robot.":
- "Totally fair! I'm here to get things started and make the process easier. You'll still get to speak with a licensed agent."

WHEN CALLER GETS ANGRY:
- "I understand this is frustrating. Let's see how I can help—then I'll bring in a specialist if needed."
- Stay calm and empathetic
- Offer to escalate to human agent

WHEN CALLER TRIES TO RUSH:
- "I'll keep this super quick—can I just confirm your name and zip code to check availability?"

WHEN CALLER IS SKEPTICAL:
- "I completely understand being cautious. We're licensed agents at Inshora Group, and I'm here to help you find the best coverage at the best price."

WHEN CALLER MENTIONS COMPETITOR:
- "That's great that you're shopping around! Let me see if we can match or beat that—what coverage did they offer?"
"""

# ===========================
# COMBINED KNOWLEDGE BASE
# ===========================

INSHORA_KNOWLEDGE_BASE = f"""
=== INSHORA GROUP AI KNOWLEDGE BASE ===

{TEXAS_INSURANCE_LAWS}

{OBJECTION_HANDLING}

{ESCALATION_PROTOCOLS}

{LEAD_SCORING}

{TONE_ADAPTATION}

{PROMOTIONS_DISCOUNTS}

{REBUTTALS}

=== END OF KNOWLEDGE BASE ===
"""


def get_knowledge_base() -> str:
    """Return the complete knowledge base as a string."""
    return INSHORA_KNOWLEDGE_BASE


def get_texas_laws() -> str:
    """Return Texas-specific insurance laws."""
    return TEXAS_INSURANCE_LAWS


def get_objection_handling() -> str:
    """Return objection handling scripts."""
    return OBJECTION_HANDLING


def get_escalation_protocols() -> str:
    """Return escalation protocols."""
    return ESCALATION_PROTOCOLS


def get_lead_scoring() -> str:
    """Return lead scoring matrix."""
    return LEAD_SCORING


def get_tone_adaptation() -> str:
    """Return tone adaptation guidelines."""
    return TONE_ADAPTATION


def get_promotions() -> str:
    """Return current promotions and discounts."""
    return PROMOTIONS_DISCOUNTS


def get_rebuttals() -> str:
    """Return rebuttal scripts."""
    return REBUTTALS

