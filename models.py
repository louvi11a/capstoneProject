# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Archivedfiles(models.Model):
    # Field name made lowercase.
    archivedfileid = models.AutoField(
        db_column='archivedfileID', primary_key=True)
    # Field name made lowercase.
    fileid = models.ForeignKey(
        'Orphanfiles', models.DO_NOTHING, db_column='fileID', blank=True, null=True)
    # Field name made lowercase.
    filename = models.CharField(
        db_column='fileName', max_length=255, blank=True, null=True)
    # Field name made lowercase.
    filedescription = models.CharField(
        db_column='fileDescription', max_length=255, blank=True, null=True)
    # Field name made lowercase.
    filepath = models.TextField(db_column='filePath', blank=True, null=True)
    is_archived = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'archivedFiles'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey(
        'DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class NotesNlpresult(models.Model):
    id = models.BigAutoField(primary_key=True)
    noun_phrase = models.CharField(max_length=255, blank=True, null=True)
    verb = models.CharField(max_length=255, blank=True, null=True)
    note = models.ForeignKey('NotesNote', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'notes_nlpresult'


class NotesNote(models.Model):
    # Field name made lowercase.
    orphanid = models.IntegerField(db_column='orphanID')
    text = models.TextField()
    sentiment_score = models.FloatField(blank=True, null=True)
    timestamp = models.DateTimeField()
    translated_note = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'notes_note'


class Orphanbehavior(models.Model):
    # Field name made lowercase.
    behaviorid = models.AutoField(db_column='behaviorID', primary_key=True)
    # Field name made lowercase.
    behaviordate = models.DateField(
        db_column='behaviorDate', blank=True, null=True)
    # Field name made lowercase.
    behaviornotes = models.TextField(
        db_column='behaviorNotes', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'orphanBehavior'


class Orphanfiles(models.Model):
    # Field name made lowercase.
    fileid = models.AutoField(db_column='fileID', primary_key=True)
    # Field name made lowercase.
    filename = models.CharField(
        db_column='fileName', max_length=255, blank=True, null=True)
    # Field name made lowercase.
    filedescription = models.TextField(
        db_column='fileDescription', blank=True, null=True)
    # Field name made lowercase.
    filepath = models.CharField(
        db_column='filePath', max_length=255, blank=True, null=True)
    is_archived = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'orphanFiles'


class Orphaninfo(models.Model):
    # Field name made lowercase.
    orphanid = models.AutoField(db_column='orphanID', primary_key=True)
    # Field name made lowercase.
    firstname = models.CharField(
        db_column='firstName', max_length=255, blank=True, null=True)
    # Field name made lowercase.
    middlename = models.CharField(
        db_column='middleName', max_length=255, blank=True, null=True)
    # Field name made lowercase.
    lastname = models.CharField(
        db_column='lastName', max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=1, blank=True, null=True)
    # Field name made lowercase.
    birthdate = models.DateField(db_column='birthDate', blank=True, null=True)
    # Field name made lowercase.
    dateadmitted = models.DateField(
        db_column='dateAdmitted', blank=True, null=True)
    # Field name made lowercase.
    note = models.ForeignKey(
        Orphanbehavior, models.DO_NOTHING, db_column='orphanbehaviorID')
    # Field name made lowercase.
    orphanfileid = models.ForeignKey(
        Orphanfiles, models.DO_NOTHING, db_column='orphanFileID')
    ethnicity = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'orphanInfo'


class BMI(models.Model):
    # Field name made lowercase.
    bmi_ID = models.AutoField(db_column='bmi_ID', primary_key=True)
    # Field name made lowercase.
    orphanid = models.ForeignKey(
        Orphaninfo, models.DO_NOTHING, db_column='orphanID', blank=True, null=True)
    height_cm = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True)
    weight_kg = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True)
    # Field name made lowercase.
    bmi_category = models.CharField(
        db_column='BMI_category', max_length=255, blank=True, null=True)
    incident_count = models.IntegerField(blank=True, null=True)
    incident_type = models.CharField(max_length=255, blank=True, null=True)
    recorded_at = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'physical_health'


class SchoolSubjects(models.Model):
    # Field name made lowercase.
    subjectid = models.AutoField(db_column='subjectID', primary_key=True)
    subject_name = models.CharField(max_length=255, blank=True, null=True)
    subject_code = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'school_subjects'


class StudentGrades(models.Model):
    # Field name made lowercase.
    gradeid = models.AutoField(db_column='gradeID', primary_key=True)
    # Field name made lowercase.
    studentid = models.ForeignKey(
        'Students', models.DO_NOTHING, db_column='studentID', blank=True, null=True)
    # Field name made lowercase.
    subjectid = models.ForeignKey(
        SchoolSubjects, models.DO_NOTHING, db_column='subjectID', blank=True, null=True)
    grade = models.DecimalField(
        max_digits=5, decimal_places=3, blank=True, null=True)
    date_achieved = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'student_grades'


class Students(models.Model):
    # Field name made lowercase.
    studentid = models.AutoField(db_column='studentID', primary_key=True)
    grade_level = models.IntegerField(blank=True, null=True)
    # Field name made lowercase.
    orphanid = models.ForeignKey(
        Orphaninfo, models.DO_NOTHING, db_column='orphanID', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'students'
