from django.db import models


# Create your models here.


# class Notes(models.Model):
#     note_id = models.AutoField(primary_key=True)
#     # orphan_id = models.IntegerField()
#     text = models.TextField()
#     translated_note = models.TextField(blank=True, null=True)  # English notes
#     sentiment_score = models.FloatField(null=True)  # Allow NULL values
#     timestamp = models.DateTimeField(auto_now_add=True)

#     related_orphan = models.ForeignKey(
#         'orphans.Info', on_delete=models.CASCADE, related_name='notes')

#     def __str__(self):
#         return f"Note #{self.id} (Orphan ID: {self.orphanID})"

#     class Meta:
#         db_table = "OrphanBehavior_notes"
