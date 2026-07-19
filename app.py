"""
Spark TRL/CRL Screening Tool — public, no login, nothing stored.

Runs identically on a laptop (python app.py) and on Render (gunicorn app:app).
No database and no password: this is a public screening front door, and by design
nothing the user enters is saved or transmitted to Spark.
"""
import os
from flask import Flask, render_template, request, jsonify
from scoring import CATEGORIES, screen, STAGES

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "spark-screen-local")

# The seven categories, each with its five statements (verbatim from the workbook).
QUESTIONS = [
    ("technology", "Technology", [
        "The underlying research has been translated into a defined technology concept.",
        "Applied research is underway, and one or more practical applications have been identified.",
        "Laboratory testing of individual components supports the technical feasibility of the concept.",
        "The principal components have been integrated and tested under laboratory conditions.",
        "An integrated laboratory-scale system has demonstrated performance under conditions relevant to the intended application.",
    ]),
    ("product_development", "Product Development", [
        "The company has defined the initial product concept, target customer, and market need.",
        "A pilot-scale product or system has been tested in its intended application.",
        "A full-scale prototype has been demonstrated in its intended application.",
        "A near-final product or system has performed successfully under conditions representative of expected operation.",
        "The final product or system has been operated successfully across the full range of expected conditions.",
    ]),
    ("product_definition", "Product Definition / Design", [
        "The company has defined one or more testable product hypotheses.",
        "Customer needs have been translated into product attributes that support a clear value proposition.",
        "The product or system has advanced from laboratory to pilot scale, and the barriers to full-scale operation have been identified.",
        "The company has defined the customer value proposition, design specifications, certification requirements, and principal engineering trade-offs.",
        "Design work is complete, required certifications are in hand, and the final configuration reflects validated customer and product requirements.",
    ]),
    ("competitive_landscape", "Competitive Landscape", [
        "Secondary research has identified potential applications, target markets, and competing approaches.",
        "Primary market research has tested commercial feasibility and established a basic understanding of competing products and systems.",
        "Comprehensive market research supports commercial feasibility and provides a substantive understanding of competing products and systems.",
        "A structured competitive analysis demonstrates the product's distinctive features and advantages relative to available alternatives.",
        "The company has a comprehensive, evidence-based understanding of the target market, customer applications, competing offerings, and competitive dynamics.",
    ]),
    ("team", "Team", [
        "The effort is led by one individual and has not yet formed a legal entity or operating team.",
        "The company is led solely by technical or business founders, without outside advisors or support.",
        "The founding team remains weighted toward either technical or commercial capability but receives active support from advisors, mentors, or an entrepreneurial support program.",
        "The leadership team includes both technical and commercialization experience and is supported by experienced outside advisors.",
        "The company has the leadership and operating capabilities required across technology, sales, marketing, customer support, and operations, with appropriate outside guidance.",
    ]),
    ("go_to_market", "Go-to-Market", [
        "The company has defined an initial business model and the value proposition the product delivers.",
        "Customer and partner interviews have been used to refine the business model and value proposition.",
        "Customer and market requirements are defined, linked to product requirements, and supported by early relationships with key participants across the value chain.",
        "The company has established working relationships with the suppliers, partners, service providers, and customers required to enter the market.",
        "Key supplier and partner agreements are in place, and the company has received initial customer purchase orders.",
    ]),
    ("manufacturing", "Manufacturing and Value Chain", [
        "The company has mapped the suppliers, partners, and customers needed to move the product from production through delivery and use.",
        "The company has established relationships with potential suppliers, partners, service providers, and customers and incorporated their input into product and manufacturability requirements.",
        "The manufacturing process and quality requirements have been defined, and qualification activities are underway.",
        "Pilot units have been manufactured through the intended production process and sold to initial customers.",
        "The company can manufacture at commercial scale and has deployed the product broadly to customers or end users.",
    ]),
]

STAGE_LABELS = [s[1] for s in STAGES]  # 5 names
STAGE_DESCS = [s[2] for s in STAGES]


@app.route("/")
def index():
    return render_template(
        "index.html",
        questions=QUESTIONS,
        stage_labels=STAGE_LABELS,
        stage_descs=STAGE_DESCS,
    )


@app.route("/score", methods=["POST"])
def score():
    data = request.get_json(force=True) or {}
    sliders = {}
    for cat in CATEGORIES:
        try:
            v = int(data.get(cat, 0))
        except (TypeError, ValueError):
            v = 0
        sliders[cat] = max(0, min(5, v))
    result = screen(sliders)
    result["stage_labels"] = STAGE_LABELS
    result["stage_descs"] = STAGE_DESCS
    return jsonify(result)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
