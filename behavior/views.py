from deep_translator import GoogleTranslator
from django.shortcuts import redirect, render
from behavior.forms import NoteForm
import spacy
from textblob import TextBlob
from behavior.models import Notes
from orphans.models import Info  # from .models import Orphan

# imitial practice progress


# def analyze_sentiment(text):
#     blob = TextBlob(text)
#     return blob.sentiment.polarity


# def handle_note_submission(request):
#     if request.method == 'POST':
#         form = NoteForm(request.POST)
#         if form.is_valid():
#             text = form.cleaned_data['text']
#             note = prac_notes.objects.create(text=text)

#         # Translate the text to English
#         translated_text = GoogleTranslator(
#             source='ceb', target='english').translate(text)

#         # Perform sentiment analysis
#         sentiment = analyze_sentiment(translated_text)

#         # Store the sentiment result and translated text in the database
#         note = prac_notes.objects.create(
#             text=text, translated_text=translated_text, sentiment=sentiment)

#         # Store the sentiment result in the database
#         note.sentiment = sentiment
#         note.save()

#         # Redirect to a success page or something similar
#         return redirect('orphan')
#     else:
#         form = NoteForm()

#     return render(request, 'notes/note_form.html', {'form': form})


def add_note(request, orphan_id):
    orphan = Info.objects.get(orphanID=orphan_id)  # Fetch the Orphan instance
    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)  # Don't save the form yet
            bisaya_text = note.text  # Get the Bisaya text

            try:
                # Translate the Bisaya text to English
                translated_text = GoogleTranslator(
                    source='ceb', target='english').translate(bisaya_text)

                # Conduct sentiment analysis using TextBlob
                blob = TextBlob(translated_text)
                sentiment = blob.sentiment.polarity

                # Save the Bisaya text, translated text, and sentiment to the Note instance
                note.text = bisaya_text
                note.translated_note = translated_text
                note.sentiment_score = sentiment
                # Set the related_orphan foreign key to the Info instance
                note.related_orphan = orphan

                note.save()
            except Exception as e:
                # Handle any errors that occurred during the translation or sentiment analysis process
                print(f"An error occurred: {e}")
    else:
        form = NoteForm()
    return render(request, 'orphans/orphan-content.html', {'form': form, 'orphan': orphan})
