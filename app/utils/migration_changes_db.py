from app.models import *

all_services = Service.objects.all()

for service in all_services:
    mappings = LocationServiceMapping.objects.filter(service=service)
    for m in mappings:
        m.delivery_charges=service.delivery_charges
        m.delivery_min_amount=service.delivery_min_amount
        m.delivery_time_min=service.delivery_time_min
        m.display_order=service.display_order
        m.operating_time_start=service.operating_time_start
        m.operating_time_end=service.operating_time_end
        m.save()
