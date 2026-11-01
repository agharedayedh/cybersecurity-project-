from django.db import migrations, models
import django.db.models.deletion
class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(name='Member',fields=[('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('username',models.CharField(max_length=80,unique=True)),('password',models.CharField(max_length=255))]),
        migrations.CreateModel(name='Entry',fields=[('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('title',models.CharField(max_length=150)),('body',models.TextField()),('created_at',models.DateTimeField(auto_now_add=True)),('owner',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,to='journal.member'))]),
    ]
