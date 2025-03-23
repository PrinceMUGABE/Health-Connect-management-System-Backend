from django.core.management.base import BaseCommand
from appointmentApp.tasks import check_expired_appointments

class Command(BaseCommand):
    help = 'Check and update expired appointments'

    def handle(self, *args, **kwargs):
        self.stdout.write("Checking for expired appointments...")
        check_expired_appointments()
        self.stdout.write(self.style.SUCCESS('Successfully checked appointments.'))