# Generated by Django 2.1.7 on 2019-07-01 23:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('grau', models.CharField(default='Licenciatura', max_length=200)),
                ('credits_number', models.IntegerField(null=True)),
                ('credits_numberByYear', models.CharField(max_length=200, null=True)),
                ('duration', models.IntegerField(null=True)),
                ('timetable', models.CharField(max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Course_Faculdade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='university.Course')),
            ],
        ),
        migrations.CreateModel(
            name='Course_MiniCourse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('credits_number', models.IntegerField(null=True)),
                ('year', models.IntegerField(default=0)),
                ('semestres', models.CharField(max_length=200, null=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='university.Course')),
                ('miniCourse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='miniCourso', to='university.Course')),
            ],
        ),
        migrations.CreateModel(
            name='Course_SchoolYear',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='university.Course')),
            ],
        ),
        migrations.CreateModel(
            name='CourseSubject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField(default=0)),
                ('semester', models.IntegerField(default=0)),
                ('type', models.CharField(default='Semestral', max_length=200)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='university.Course')),
            ],
        ),
        migrations.CreateModel(
            name='Faculdade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Faculdade de Ciências', max_length=200)),
                ('sigla', models.CharField(default='FC', max_length=200)),
                ('link', models.CharField(default='https://ciencias.ulisboa.pt/', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(default='T', max_length=200)),
                ('turma', models.CharField(default='', max_length=200)),
                ('week_day', models.CharField(max_length=200, null=True)),
                ('hour', models.CharField(max_length=200, null=True)),
                ('duration', models.CharField(max_length=200, null=True)),
                ('is_open', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['subject__name'],
            },
        ),
        migrations.CreateModel(
            name='LessonSystemUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('presente', models.BooleanField()),
                ('date', models.DateField()),
                ('lesson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='university.Lesson')),
            ],
        ),
        migrations.CreateModel(
            name='PersonalInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=200, null=True)),
                ('birth_date', models.DateField(null=True)),
                ('name', models.CharField(max_length=200, null=True)),
                ('phone_number', models.CharField(max_length=200, null=True)),
                ('personal_email', models.CharField(max_length=200, null=True, unique=True)),
                ('gender', models.CharField(max_length=200, null=True)),
                ('nationality', models.CharField(max_length=200, null=True)),
                ('id_document', models.CharField(max_length=200, null=True, unique=True)),
                ('vat_number', models.CharField(max_length=200, null=True, unique=True)),
                ('profile_pic', models.CharField(max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(max_length=200, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room_number', models.CharField(max_length=200, unique=True)),
                ('can_give_class', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='SchoolYear',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('begin', models.IntegerField(unique=True)),
                ('end', models.IntegerField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('credits_number', models.IntegerField(default=6)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='SystemUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='university.Role')),
                ('rooms', models.ManyToManyField(blank=True, to='university.Room')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SystemUser_Faculdade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('faculdade', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='university.Faculdade')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='university.SystemUser')),
            ],
        ),
        migrations.CreateModel(
            name='SystemUser_SchoolYear',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('school_year', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='university.SchoolYear')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='university.SystemUser')),
            ],
        ),
        migrations.CreateModel(
            name='SystemUserCourse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estadoActual', models.CharField(max_length=200, null=True)),
                ('anoLectivoDeInício', models.CharField(max_length=200, null=True)),
                ('anoActual', models.IntegerField(null=True)),
                ('totalCred', models.IntegerField(default=0)),
                ('minor', models.CharField(default='Nao admitido', max_length=200)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='university.Course')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='university.SystemUser')),
            ],
        ),
        migrations.CreateModel(
            name='SystemUserMensagens',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('turmaInicial', models.CharField(max_length=200)),
                ('turmaFinal', models.CharField(max_length=200)),
                ('is_accepted', models.BooleanField(null=True)),
                ('destinatario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='destinatario', to='university.SystemUser')),
                ('remetente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='university.SystemUser')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='university.Subject')),
            ],
        ),
        migrations.CreateModel(
            name='SystemUserSubject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subjSemestre', models.IntegerField(null=True)),
                ('state', models.IntegerField(null=True)),
                ('grade', models.FloatField(null=True)),
                ('turmas', models.CharField(max_length=200, null=True)),
                ('anoLetivo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='university.SchoolYear')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='university.Subject')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='university.SystemUser')),
            ],
        ),
        migrations.AddField(
            model_name='subject',
            name='regente',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='university.SystemUser'),
        ),
        migrations.AddField(
            model_name='personalinfo',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='university.SystemUser'),
        ),
        migrations.AddField(
            model_name='lessonsystemuser',
            name='systemUser',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='university.SystemUser'),
        ),
        migrations.AddField(
            model_name='lesson',
            name='professor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='university.SystemUser'),
        ),
        migrations.AddField(
            model_name='lesson',
            name='room',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='university.Room'),
        ),
        migrations.AddField(
            model_name='lesson',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='university.Subject'),
        ),
        migrations.AddField(
            model_name='coursesubject',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='university.Subject'),
        ),
        migrations.AddField(
            model_name='course_schoolyear',
            name='school_year',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='university.SchoolYear'),
        ),
        migrations.AddField(
            model_name='course_faculdade',
            name='faculdade',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='university.Faculdade'),
        ),
        migrations.AddField(
            model_name='course',
            name='coordinator',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='university.SystemUser'),
        ),
    ]
