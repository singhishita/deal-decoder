import json

import streamlit as st
from google import genai

MODEL = "gemini-flash-latest"

PHASES = [
    "Strategy & targeting",
    "Diligence",
    "Signing to close",
    "Day 1",
    "Integration / separation",
]

EXAMPLES = ["TSA", "Stranded costs", "Clean room", "Day 1 readiness"]

st.set_page_config(page_title="Deal Decoder", page_icon="💼", layout="centered")
st.title("Deal Decoder")
st.caption("M&A and consulting vocabulary — what it means, where it sits, what you do about it.")
st.caption("Made by Ishita Singh")

api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    st.error("No API key found. Add GEMINI_API_KEY in this app's Secrets settings.")
    st.stop()

client = genai.Client(api_key=api_key)

PROMPT = """You are a senior M&A consultant explaining transaction vocabulary precisely.

Ground your answer in standard, widely-documented transaction practice — the vocabulary
common across corporate development, transaction services and integration work. Use knowledge from publicly posted content from McKinsey, Bain, BCG, EY, Deloitte, and similar firms. Do not
invent firm-specific methodologies or cite proprietary frameworks. If a term is used
differently across contexts, say so rather than picking one arbitrarily.

STEP 1 — Validity. Decide whether the input is a real term used in M&A, corporate
finance, transaction services, or management consulting. Gibberish, random characters,
or terms from entirely unrelated fields are NOT valid.

If NOT valid, return ONLY:
  {{"is_valid_term": false, "term": "<what they typed>"}}

STEP 2 — If valid, classify it into exactly ONE concept type:
- Deal structure — how the transaction itself is legally or financially arranged
- Process or phase — a stage, milestone, or activity in the deal lifecycle
- Financial concept — a value, cost, or accounting idea
- Workstream artifact — a document, plan, or deliverable produced during a deal
- Risk or issue — something that can go wrong and must be managed
- Role or party — a person, team, or entity involved in the transaction

STEP 3 — Map it to deal phases. Choose every phase where the term is actively relevant,
from this exact list: {phases}

STEP 4 — Explain it for this audience: {audience}

Return ONLY valid JSON. No markdown fences, no commentary. Exactly these keys:
  is_valid_term (true)
  term (string, properly capitalised)
  also_known_as (string, common alternative names or abbreviations; empty string if none)
  concept_type (string, one of the six above)
  phases (list of strings, from the phase list above)
  definition (string, 2-3 sentences)
  why_it_matters (string, 2 sentences on the commercial or operational stakes)
  what_you_actually_do (list of exactly 3 strings, concrete actions a consultant takes)
  it_workstream_angle (string, 1-2 sentences on how this shows up specifically in IT
    and technology workstreams; if it genuinely has no IT dimension, say so plainly)
  common_misconception (string, 1-2 sentences on what people new to deals get wrong)
  related_terms (list of exactly 3 strings)

Term: {term}"""

AUDIENCES = {
    "New to deals": (
        "Someone who has just joined a transaction team. Assume business literacy but no "
        "deal experience. Spell out acronyms on first use. Prioritise clarity over concision."
    ),
    "Brief a partner": (
        "An experienced partner who wants the sharp version. Assume full fluency in deal "
        "vocabulary. Be concise and precise. Lead with implications, not definitions."
    ),
}


def set_term(value):
    st.session_state.term = value


if "term" not in st.session_state:
    st.session_state.term = ""

st.write("**Try one:**")
cols = st.columns(len(EXAMPLES))
for col, example in zip(cols, EXAMPLES):
    col.button(example, on_click=set_term, args=(example,), use_container_width=True)

term = st.text_input(
    "Term",
    key="term",
    placeholder="e.g. carve-out, synergy capture, reverse TSA, RTB vs CTB",
)

audience = st.radio("Explain it for", list(AUDIENCES), horizontal=True)

if st.button("Decode", type="primary") and term.strip():
    with st.spinner("Decoding..."):
        response = client.models.generate_content(
            model=MODEL,
            contents=PROMPT.format(
                term=term.strip(),
                audience=AUDIENCES[audience],
                phases=", ".join(PHASES),
            ),
        )
        raw = response.text.strip()

    cleaned = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        st.warning("The model didn't return clean JSON this time. Raw output below.")
        st.code(raw)
    else:
        if not data.get("is_valid_term", True):
            st.error(
                f"'{data.get('term', term)}' doesn't look like a deal or consulting term. "
                "Try something like TSA, carve-out, or synergy capture."
            )
        else:
            st.divider()
            st.subheader(data["term"])
            if data.get("also_known_as"):
                st.caption(f"Also known as: {data['also_known_as']}")

            st.markdown(f"**{data['concept_type']}**")
            st.write(data["definition"])

            st.markdown("**Where it sits in the deal**")
            active = set(data.get("phases", []))
            phase_cols = st.columns(len(PHASES))
            for col, phase in zip(phase_cols, PHASES):
                if phase in active:
                    col.success(phase)
                else:
                    col.caption(phase)

            st.markdown("**Why it matters**")
            st.write(data["why_it_matters"])

            st.markdown("**What you actually do about it**")
            for action in data["what_you_actually_do"]:
                st.markdown(f"- {action}")

            st.info(f"**IT workstream angle** — {data['it_workstream_angle']}")

            st.warning(f"**Commonly misunderstood** — {data['common_misconception']}")

            st.markdown("**Related terms:** " + ", ".join(data["related_terms"]))

        with st.expander("See the raw model output"):
            st.code(raw)

st.divider()
st.caption(
    "Explanations are AI-generated from general transaction practice and may contain "
    "errors. Not a substitute for firm methodology or professional advice."
)
