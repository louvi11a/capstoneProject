from deep_translator import GoogleTranslator
from django.shortcuts import redirect, render
from behavior.forms import NoteForm
import spacy
from textblob import TextBlob
from behavior.models import prac_notes
# imitial practice progress


def analyze_sentiment(text):
    blob = TextBlob(text)
    return blob.sentiment.polarity


def handle_note_submission(request):
    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            note = prac_notes.objects.create(text=text)

        # Translate the text to English
        translated_text = GoogleTranslator(
            source='ceb', target='english').translate(text)

        # Perform sentiment analysis
        sentiment = analyze_sentiment(translated_text)

        # Store the sentiment result and translated text in the database
        note = prac_notes.objects.create(
            text=text, translated_text=translated_text, sentiment=sentiment)

        # Store the sentiment result in the database
        note.sentiment = sentiment
        note.save()

        # Redirect to a success page or something similar
        return redirect('orphan')
    else:
        form = NoteForm()

    return render(request, 'notes/note_form.html', {'form': form})


# non practice but cannot commnt out so ani lang sa sya kay mag error
def add_note(request):
    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)  # Don't save the form yet
            bisaya_text = note.text  # Get the Bisaya text

            # Translate the Bisaya text to English
            translated_text = GoogleTranslator(
                source='ceb', target='english').translate(bisaya_text)

            # Conduct NLP using spaCy
            # Load English tokenizer, tagger, parser, NER and word vectors
            nlp = spacy.load('en_core_web_sm')
            doc = nlp(translated_text)  # Process whole documents

            # Analyze syntax
            # Noun phrases
            noun_phrases = [chunk.text for chunk in doc.noun_chunks]
            verbs = [token.lemma_ for token in doc if token.pos_ ==
                     "VERB"]  # Verbs

            # Save the NLP result to the Note instance
            # This is just an example, you might want to format the result differently
            note.nlp_result = f"Noun phrases: {noun_phrases}, Verbs: {verbs}"

            note.save()
    else:
        form = NoteForm()
    return render(request, 'notes/note_form.html', {'form': form})
