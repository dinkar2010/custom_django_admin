from app.models import *

offer = Offer.objects.all()[0]
offerproductMapping = offer.offerproductmapping_set.all()[0]
all_ordered_products  = offerproductMapping.product.orderedproduct_set.all()
for a in all_ordered_products:
    device_id =  a.cart.order.user.userprofile.device_id
    order = a.cart.order
    OfferProductOrderMapping(order=order,device_id=device_id,offer_product=offerproductMapping).save()