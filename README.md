# Deal Decoder

Paste a term from the M&A world — get back what kind of concept it is, where it sits
in the deal lifecycle, what you actually do about it, and what people new to deals
typically get wrong.

**Live app:** https://deal-decoder.streamlit.app

## Why

Transaction vocabulary is learned by osmosis. You hear "we'll handle it under the TSA"
in your first week and nod. This makes the implicit explicit — and maps each term to the
phase of the deal where it actually matters, which is the part that's hardest to pick up
from reading.

Two audience modes: one for people who just joined a transaction team, one for the
sharper version you'd bring to a partner conversation.

## How it works

1. Streamlit collects the term and the target audience
2. A multi-step prompt asks Gemini to validate the term, classify it, map it to deal
   phases from a fixed list defined in the code, and explain it for the chosen audience
3. Strict JSON comes back and renders as structured output, with a fallback if the model
   returns something malformed

The deal-phase taxonomy lives in the Python code, not the prompt's imagination — the app
owns the categories, the model does the reasoning.

## Stack

Python · Streamlit · Google Gemini API · deployed on Streamlit Community Cloud

## Run it yourself

```
pip install -r requirements.txt
streamlit run app.py
```
 
Add your Gemini key to `.streamlit/secrets.toml`:
 
```
GEMINI_API_KEY = "your-key"
```
 
## Accuracy
 
Explanations are generated from the model's knowledge of general, publicly-documented
transaction practice. No proprietary methodology or client material is used anywhere in
this project. Output may contain errors and is not a substitute for firm guidance or
professional advice.
 
## What I'd do next
 
- Ground the definitions in a curated glossary rather than model knowledge alone
- Build an eval set of 25 terms with expert-checked answers, and score against it
- Add a comparison mode for term pairs like RTB vs CTB
```
