from app.models import *

lsm = LocationServiceMapping.objects.all()[0]
ts = TimeSlot.objects.all()[0]#(start_time=lsm.operating_time_start,end_time=lsm.operating_time_end)
ts.save()
sps = StoreProductMapping.objects.all()
for sp in sps:
    service = sp.product.product.category.service
    store = sp.store
    if service not in store.services.all():
        store.services.add(service)

lsms = LocationServiceMapping.objects.all()
for lsm in lsms:
    location = lsm.location
    service = lsm.service
    dc = lsm.delivery_charges
    mda = lsm.delivery_min_amount
    mdt = lsm.delivery_time_min
    stores = location.store_set.all()
    for store in stores:
        if service in store.services.all():
            stl = StoreTimingInLocation(lsm=lsm,store=store,delivery_charges=dc,delivery_min_amount=mda,normal_hours_delivery_time_min=mdt,rush_hours_delivery_time_min=mdt)
            stl.save()
            stl.time_slot.add(ts)
            stl.save()
