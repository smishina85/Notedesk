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
        # print(cat)
        # print(type(cat))
        # print(cat[0])
        try:
            category = Category.objects.get(name_cat = cat )
            # print(type(category))
            notes_categorized = Note.objects.filter(categ=cat)
            # print(type(news_categorized))
            notes_quantity = notes_categorized.count()
            # print(news_quantity)
            if notes_quantity:
                self.stdout.readable()
                self.stdout.write(f'The are {notes_quantity} notes in category {cat}. Do you really want to delete them ? yes/no')
                answer = input()
                if answer == 'yes':
                    # news_categorized.all().delete()
                    # for news in news_categorized:
                    #     # print(news.id)
                    #     # print((Post.objects.get(id=news.id)).id)
                    #     Post.objects.get(id=news.id).delete()
                        # self.stdout.write(self.style.SUCCESS('Successfully deleted news "%s"' % str(news)))
                    notes_categorized.delete()
                    self.stdout.write(self.style.SUCCESS(f'All notes of the category {cat} deleted'))
                    return
                self.stdout.write(self.style.ERROR('Access denied'))
        except ObjectDoesNotExist:
            self.stdout.write('Wrong parameter or such category does not exist')

        # self.stdout.write(str(options['category']))





