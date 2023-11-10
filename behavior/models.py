from django.db import models


# Create your models here.


class Notes(models.Model):
    note_id = models.AutoField(primary_key=True)
    orphan_id = models.IntegerField()
    text = models.TextField()
    translated_note = models.TextField(blank=True, null=True)  # English notes
    sentiment_score = models.FloatField(null=True)  # Allow NULL values
    timestamp = models.DateTimeField(auto_now_add=True)

    related_orphan = models.ForeignKey(
        'orphans.Info', on_delete=models.CASCADE, related_name='notes')

    def __str__(self):
        return f"Note #{self.id} (Orphan ID: {self.orphanID})"

    # class Meta:
    #     db_table = "your_custom_table_name"


class NLPResult(models.Model):
    notes = models.ForeignKey(
        Notes, on_delete=models.CASCADE, related_name='nlp_results')
    noun_phrase = models.CharField(max_length=255, blank=True, null=True)
    verb = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"NLP Result for Note #{self.notes.id}"


class prac_notes(models.Model):
    text = models.TextField()
    translated_text = models.TextField(
        blank=True, null=True)  # New field for translated text
    sentiment = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'practice_notes'
