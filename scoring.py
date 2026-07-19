"""
Spark TRL/CRL screening engine.

Replicates the exact gated logic from the Spark_TRL_CRL_Calculator workbook.
Seven category sliders (1-5) drive two gated 1-9 scores: TRL and CRL.

The public tool only ever DISPLAYS a 1-5 stage read (see stage_from_score).
The true 1-9 scores are computed here but never surfaced to the user, by design.
"""

# ---- Category keys (the 7 workbook sliders) ----
CATEGORIES = [
    "technology",              # K21
    "product_development",     # K30
    "product_definition",      # K39
    "competitive_landscape",   # K48
    "team",                    # K57
    "go_to_market",            # K66
    "manufacturing",           # K75
]

# threshold-flag helper: L-cell = 1 when that category's slider >= n
def _f(sliders, cat, n):
    return 1 if sliders.get(cat, 0) >= n else 0


def true_trl(sliders):
    """Gated TRL 1-9, exactly per workbook O-column logic."""
    t = lambda cat, n: _f(sliders, cat, n)
    # O31..O23 top-down; return highest satisfied level
    if t("product_development", 5): return 9                                  # L35
    if t("product_development", 4): return 8                                  # L34
    if t("product_development", 3): return 7                                  # L33
    if t("product_development", 2) and t("product_definition", 3): return 6   # L32 & L42
    if t("technology", 5): return 5                                           # L26
    if t("technology", 4): return 4                                           # L25
    if t("technology", 3): return 3                                           # L24
    if t("technology", 2): return 2                                           # L23
    if t("technology", 1): return 1                                           # L22
    return 0


def true_crl(sliders):
    """Gated CRL 1-9, exactly per workbook Q-column logic (all-AND gates)."""
    t = lambda cat, n: _f(sliders, cat, n)
    # Q31..Q23 top-down
    if t("team", 5) and t("manufacturing", 5): return 9                       # L62 & L80
    if t("team", 5) and t("manufacturing", 4): return 8                       # L62 & L79
    if t("team", 4) and t("go_to_market", 5) and t("manufacturing", 3): return 7   # L61,L71,L78
    if t("product_definition", 5) and t("team", 4) and t("go_to_market", 4): return 6  # L44,L61,L70
    if t("product_definition", 4) and t("competitive_landscape", 5) and t("team", 3) \
       and t("go_to_market", 3) and t("manufacturing", 2): return 5          # L43,L53,L60,L69,L77
    if t("product_definition", 2) and t("competitive_landscape", 4) and t("team", 3) \
       and t("go_to_market", 2) and t("manufacturing", 1): return 4          # L41,L52,L60,L68,L76
    if t("product_development", 1) and t("product_definition", 1) \
       and t("competitive_landscape", 3) and t("team", 2) and t("go_to_market", 1): return 3  # L31,L40,L51,L59,L67
    if t("competitive_landscape", 2) and t("team", 2): return 2              # L50 & L59
    if t("competitive_landscape", 1) and t("team", 1): return 1              # L49 & L58
    return 0


# ---- 1-9 -> 1-5 display stage mapping (public-facing) ----
# Honest banding: nine true levels collapse into five named screening stages.
STAGES = [
    (1, "Early Stage",  "Concept and early validation"),
    (2, "Exploration",  "Applied research and first customers"),
    (3, "Development",  "Building and testing in real conditions"),
    (4, "Readiness",    "Near-final, entering the market"),
    (5, "Deployment",   "Operating and scaling commercially"),
]

def stage_from_score(score_1_9):
    """Collapse a true 1-9 score into a 1-5 screening stage number."""
    if score_1_9 <= 0:
        return 0
    # 1-2 -> 1, 3-4 -> 2, 5-6 -> 3, 7-8 -> 4, 9 -> 5
    mapping = {1:1, 2:1, 3:2, 4:2, 5:3, 6:3, 7:4, 8:4, 9:5}
    return mapping[score_1_9]


# Action-phrased next milestones, one per current stage, per scale.
# The milestone describes what to do to reach the NEXT stage. Stage 5 is terminal.
TRL_MILESTONES = {
    1: "Begin applied research and identify the practical applications the technology can serve.",
    2: "Integrate and test the principal components under conditions representative of the intended application.",
    3: "Demonstrate a full-scale prototype and prove near-final performance under expected operating conditions.",
    4: "Operate the final system across the full range of expected conditions to confirm readiness.",
    5: "Sustain full-scale operation and hold performance as deployment scales.",
}
CRL_MILESTONES = {
    1: "Test commercial feasibility through market research and build the founding team's core capability.",
    2: "Validate customer requirements, refine the business model, and establish the relationships required to enter the market.",
    3: "Convert market relationships into supply agreements and secure the company's first customer orders.",
    4: "Build the operating capabilities and manufacturing readiness to deliver at commercial scale.",
    5: "Scale commercial operation and broaden deployment across the customer base.",
}


def screen(sliders):
    """Public result: 1-5 stage for TRL and CRL. True scores kept internal."""
    trl9 = true_trl(sliders)
    crl9 = true_crl(sliders)
    trl_stage = stage_from_score(trl9)
    crl_stage = stage_from_score(crl9)
    return {
        "trl_stage": trl_stage,
        "crl_stage": crl_stage,
        "trl_milestone": TRL_MILESTONES.get(trl_stage, ""),
        "crl_milestone": CRL_MILESTONES.get(crl_stage, ""),
        "complete": all(sliders.get(c, 0) >= 1 for c in CATEGORIES),
        # radar uses the raw 1-5 slider positions per category
        "radar": {c: sliders.get(c, 0) for c in CATEGORIES},
    }
