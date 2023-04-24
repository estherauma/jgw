
from django.core.management.base import BaseCommand

from common.preferences import Preferences
from dashboard.models import Route


class Command(BaseCommand):
    def handle(self, *args, **options):
        preferences = Preferences()
        origin_and_destination = preferences.origin_and_destination_list()
        origin_and_destination = origin_and_destination[0:2]

        existing_routes = Route.objects.filter(
            origin_country__in=[country['origin_country'] for country in origin_and_destination],
            destination_country__in=[country['destination_country'] for country in origin_and_destination]
        )
        existing_routes.delete()

        routes_to_create = []
        for routes in origin_and_destination:
            route = Route(
                origin_country=routes['origin_country'],
                destination_country=routes['destination_country']
            )
            routes_to_create.append(route)

        # Bulk create the Route objects in the database
        Route.objects.bulk_create(routes_to_create)
