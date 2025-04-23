from django.core.management.base import BaseCommand
from core.models import CustomUser

class Command(BaseCommand):
    help = 'Updates MILTON user permissions'

    def handle(self, *args, **kwargs):
        try:
            user = CustomUser.objects.get(username='MILTON')
            user.can_upload = True
            user.can_view = True
            user.save()
            self.stdout.write(self.style.SUCCESS('Successfully updated MILTON\'s permissions'))
        except CustomUser.DoesNotExist:
            self.stdout.write(self.style.ERROR('User MILTON not found')) 