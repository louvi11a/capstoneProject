from datetime import datetime
from django.core.management.base import BaseCommand
from orphans.models import Info, Notes
from deep_translator import GoogleTranslator
from nltk.sentiment import SentimentIntensityAnalyzer
from faker import Faker
import random


class Command(BaseCommand):
    help = 'Populate database with realistic behavior notes in Bisaya, translate to English, and analyze sentiment.'

    def handle(self, *args, **options):
        fake = Faker()
        sid = SentimentIntensityAnalyzer()
        sid.lexicon.update({'shrewish': -1.0})

        bisaya_phrases = [
            "Sigi rag hilak, gamay ra nga butang dagko na kaayo og drama.",
            "Lisod ni siya pugson, kung dili niya gusto, way makapabuhat niya.",
            "Tamad kaayo ni siya, dili gyud magbuhat og assignments kon dili suruon.",
            "Wala ni siya ganaha mo eskwela, magsige lang og yawyaw nga di siya gusto moadto.",
            "Mahiyain kaayo ni siya, di ganahan makig amigo og bag-ong tawo.",
            "Wala niya kasabot ang instructions, pirmi magsige og pangutana.",
            "Pasaway ni siya kaayo, pero kugihan sab pag naa nagtan-aw niya.",
            "Sakto ra maning bataa, quiet lang sa sulod sa room.",
            "Medyo hilakero gamay, ganahan og attention.",
            "Pirmi magsigeg pangutana, curious kaayo sa palibot.",
            "Mahiyain ni siya, lisod makig-friend sa uban.",
            "Hilomon ni siya, pero bright kaayo.",
            "Maayo ni siya motabang sa mga chores.",
            "Medyo bully ni siya, pirmi manghilabot sa ubang bata."
            "Maayo mo-share ni siya sa iyang mga dulaan.",
            "Ganahan magbasa og libro, lahi ra sa ubang bata.",
            "Agresibo kaayo ni siya, pirmi mangulata og uban.",
            "Wala ni siya problema sa school, dali ra makasabot.",
            "Dali ra kaayo ni siya masuko, short-tempered."
            "Saba kaayo ni siya, pirmi lang magsigeg singgit bisan naa'y tawo nga natulog."
            "Pirmi ni siya magsige og hilak ug yawyaw kon dili mahatag iyang gusto, spoiled kaayo.",
            "Mahiyain kaayo ni siya, motago dayon kon adunay bisita ug dili ganahan makig-istorya sa mga dili niya kaila.", "Dali ra kaayo ni siya ma-distract sa iyang palibot, lisod mag focus",
            "Ganahan kaayo ni siya motabang sa balay, bisan wala siya surgoa mobuhat gyud siya og initiative.",
            "Honest kaayo ni siya, mo-admit dayon kon siya ang nakabuhat og mali.",
            "Maayo ni siya listener, mosunod dayon sa mga instructions.",
            "Mahigugmaon kaayo ni siya sa mga hayop, gentle siya mo-handle sa mga pets.",
            "Pirmi ni siya positive, mohatag og maayong vibes sa iyang palibot.",
            "Ganihang mo-comfort sa uban, maayo ni siya mo-empathize sa gibati sa lain.",
        ]

        # Define the date range explicitly as datetime objects
        start_date = datetime(2020, 1, 1)
        end_date = datetime(2023, 1, 1)

        # Attempt to translate phrases once and cache the results
        translator = GoogleTranslator(source='ceb', target='english')
        translations = {}
        for phrase in bisaya_phrases:
            try:
                translations[phrase] = translator.translate(phrase)
            except Exception as e:
                print(f"Error translating phrase: {phrase}. Error: {e}")
                # Fallback translation
                translations[phrase] = "Translation failed"

        infos = Info.objects.all()
        for info in infos:
            for _ in range(4):  # Generate 5 notes per orphan
                bisaya_text = random.choice(bisaya_phrases)
                # Use cached translation
                translated_text = translations[bisaya_text]
                sentiment = sid.polarity_scores(translated_text)
                note_timestamp = fake.date_time_between(
                    start_date=start_date, end_date=end_date)

                Notes.objects.create(
                    related_orphan=info,
                    text=bisaya_text,
                    translated_note=translated_text,
                    sentiment_score=sentiment['compound'],
                    timestamp=note_timestamp
                )

        self.stdout.write(self.style.SUCCESS(
            'Successfully populated Bisaya/Cebuano behavior notes with 5 entries per Info instance.'))
