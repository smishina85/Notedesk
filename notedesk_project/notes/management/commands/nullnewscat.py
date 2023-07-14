from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError
from notes.models import Category, Note, NoteReply

class Command(BaseCommand):
    help = 'This command deletes all notes from some category'
    missing_args_message = 'Not enough arguments'
    requires_migrations_checks = True

    def add_arguments(self, parser):
        parser.add_argument('category', nargs=1)

    def handle(self, *args, **options):
        cat = (options['category'][0]).capitalize()

        try:
            notes_categorized = Note.objects.filter(categ=cat)
            notes_quantity = notes_categorized.count()

            if notes_quantity:
                self.stdout.readable()
                self.stdout.write(f'The are {notes_quantity} notes in category {cat}. Do you really want to delete them ? yes/no')
                answer = input()
                if answer == 'yes':
                    notes_categorized.delete()
                    self.stdout.write(self.style.SUCCESS(f'All notes of the category {cat} deleted'))
                    return
                self.stdout.write(self.style.ERROR('Access denied'))
        except ObjectDoesNotExist:
            self.stdout.write('Wrong parameter or such category does not exist')






