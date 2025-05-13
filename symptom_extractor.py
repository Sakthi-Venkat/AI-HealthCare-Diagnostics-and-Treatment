import spacy

# Load the scispaCy medical NER model
nlp = spacy.load("en_ner_bc5cdr_md")

def extract_symptoms(text):
    doc = nlp(text)
    symptoms = [ent.text.lower() for ent in doc.ents if ent.label_ == "DISEASE"]
    return list(set(symptoms))  # remove duplicates
