from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password, identify_hasher
from journal.models import Member
class Command(BaseCommand):
    help = 'Run ONCE before enabling the A02 password-hash fix; hashes existing plaintext passwords.'
    def handle(self,*args,**kwargs):
        updated=0
        for member in Member.objects.all():
            try:
                identify_hasher(member.password)
            except ValueError:
                member.password=make_password(member.password)
                member.save(update_fields=['password'])
                updated+=1
        self.stdout.write(self.style.SUCCESS(f'Hashed {updated} legacy passwords. Now enable A02 fixes in views.py.'))
