from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import DjangoModelPermissions
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.utils import timezone

from core.models import CustomUser, Bike, BikeLocation, BikeRental
from core.utils import get_current_bikelocations
from api.serializers import UserSerializer, BikeSerializer, BikeLocationSerializer, StartRentalSerializer, StopRentalSerializer


class UserViewSet(viewsets.ModelViewSet):
    '''
    API endpoint for management of BaaS Users.
    Administrators can manage all users.
    Users can manage their own user.
    '''
    serializer_class = UserSerializer
    permission_classes = [DjangoModelPermissions]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return CustomUser.objects.all()
        else:
            return CustomUser.objects.filter(pk=self.request.user.pk)


class BikeViewSet(viewsets.ModelViewSet):
    '''
    API endpoint for management and usage of BaaS Bikes. 
    Fleet managers can add new bikes or update their status. 
    Bikes can update their own location.
    Users can start a bikerental session and find bikes near their location.
    '''
    queryset = Bike.objects.all()
    serializer_class = BikeSerializer
    permission_classes = [DjangoModelPermissions]

    @extend_schema(
            parameters=[
                OpenApiParameter(name='lat', description='latitude', required=True, type=float),
                OpenApiParameter(name='lng', description='longitude', required=True, type=float),
            ]
    )
    @action(detail=False, methods=['get'])
    def find_nearby(self, request):
        '''
        Lists all bikes within a 1 kilometer radius of the coordinates provided.
        '''
        self.serializer_class = BikeLocationSerializer
        lat = request.GET.get('lat')
        lng = request.GET.get('lng')
        if lat and lng:
            try:
                locations = get_current_bikelocations()
                locations = locations.filter(latitude__range = (float(lat)-0.01, float(lat)+0.01), longitude__range=(float(lng)-0.01, float(lng)+0.01))
                if locations.exists():
                    return Response(self.serializer_class(locations, many=True).data, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "Could not find any nearby bikes"}, status=status.HTTP_404_NOT_FOUND)
            except ValueError:
                return Response({"error": "Unexpected format for lat and lng query parameters"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "lat and lng query parameters not provided"}, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=False, methods=['get'])
    def find_nearest(self, request):
        '''
        Provides the bike with the nearest location for the coordinates provided.
        '''
        self.serializer_class = BikeLocationSerializer
        lat = request.GET.get('lat')
        lng = request.GET.get('lng')

        if lat and lng:
            try:
                locations = get_current_bikelocations()
                if not locations.exists:
                    return Response({"error": "Could not find any nearby bikes"}, status=status.HTTP_404_NOT_FOUND)

                nearest = locations[0]
                nearest_diff = abs(float(lat)-nearest.latitude)+abs(float(lng)-nearest.longitude)
                for location in locations[1:]:
                    diff = abs(float(lat)-location.latitude)+abs(float(lng)-location.longitude)
                    if diff < nearest_diff:
                        nearest = location
                        nearest_diff = diff
                return Response(self.serializer_class(nearest).data, status=status.HTTP_200_OK)
            except ValueError:
                return Response({"error": "Unexpected format for lat and lng query parameters"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "lat and lng query parameters not provided"}, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=True, methods=['get', 'post'])
    def location(self, request, pk=None):
        '''
        Get latest known location of a bike.
        '''
        self.serializer_class = BikeLocationSerializer
        bike = self.get_object()

        if request.method == 'GET':
            return Response(self.serializer_class(bike.location()).data, status=status.HTTP_200_OK)
        
        if request.method == 'POST':
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save(bike=bike)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=True, methods=['get',])
    def location_history(self, request, pk=None):
        '''
        Get the location history of a bike.
        '''
        self.serializer_class = BikeLocationSerializer
        locations = BikeLocation.objects.filter(bike=self.get_object())
        
        return Response(self.serializer_class(locations, many=True).data, status=status.HTTP_200_OK)
    

    @action(detail=True, methods=['get',])
    def start_rental(self, request, pk=None):
        '''
        Start a bike rental session with the specified bike. Requires an available bike and a user with an active subscription.
        '''
        self.serializer_class = StartRentalSerializer
        data = {'bike': self.get_object().pk, 'user': request.user.pk}
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=True, methods=['get'])
    def stop_rental(self, request, pk=None):
        '''
        Stop an active bike rental session with the specified bike.
        '''
        self.serializer_class = StopRentalSerializer
        rental = BikeRental.objects.filter(bike=self.get_object(), end_time__isnull=True).first()
        if rental:
            rental.end_time = timezone.now()
            rental.save()
            rental.bike.status = 'A'
            rental.bike.save()
            return Response(self.serializer_class(rental).data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "No active bikerental with this bike was found"}, status=status.HTTP_404_NOT_FOUND)