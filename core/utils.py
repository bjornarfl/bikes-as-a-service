from core.models import Bike, BikeLocation

def get_current_bikelocations():
    bikes = Bike.objects.all().prefetch_related("bikelocation_set")
    locations = []
    for bike in bikes:
        location = bike.bikelocation_set.first()
        if location is not None:
            locations.append(location.pk)
    return BikeLocation.objects.filter(pk__in=locations)