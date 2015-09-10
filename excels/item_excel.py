import xlwt
from app.models import *
from app.utils import constant


def removeNonAscii(s):
    try:
        s = unidecode(s)
    except:
        pass

    try:
        return "".join(i for i in s if ord(i) < 128)
    except:
        return ""
def my_unicode(s):

	s=removeNonAscii(s)

	if s == None:
		return s

	try:
		s = unicode(unidecode(s))
	except:
		pass

	if isinstance(s, unicode):
		return unicode(s)
	else:
		try:
			return unicode(unidecode(s.decode('utf-8')))
		except:
			return unicode(s.decode('utf-8'))
# def is_number(s):
#     try:
#         float(s)
#         return True
#     except ValueError:
#         return False
services =Service.objects.all()
book = xlwt.Workbook()
sheet = book.add_sheet("Sheet1", cell_overwrite_ok=True)
index=1
sheet.write(0,1,'ID')
sheet.write(0,1,'Brand name')
sheet.write(0,2,'Name')
sheet.write(0,3,'Size')
sheet.write(0,4,'Price')
sheet.write(0,5,'Discount')
sheet.write(0,6,'Status')
sheet.write(0,7,'Max Buy Quantity')
sheet.write(0,8,'Category')
sheet.write(0,9,'Category')
sheet.write(0,10,'Sub-Category')
sheet.write(0,11,'Image')
sheet.write(0,12,'About')
for service in services:

	cats = Category.objects.filter(parent=None,service=service)

	for cat in cats:
		print cat.name


		sub_cats = Category.objects.filter(parent=cat)
		for sub_cat in sub_cats:
			store_products = StoreProductMapping.objects.filter(store__id__in=constant.main_stores,product__product__category=sub_cat)
			for p in store_products:
				sheet.write(index,0,str(p.id))
				sheet.write(index,1,str(my_unicode(p.product.product.brand_name)))
				sheet.write(index,2,str(my_unicode(p.product.product.name)))
				sheet.write(index,3,str(p.product.size.magnitude)+" "+str(p.product.size.unit))
				sheet.write(index,4,str(p.price))
				sheet.write(index,5,str(p.discount))
				if p.stock:
					status="In Stock"
				else:
					status="Out of Stock"
				sheet.write(index,6,status)
				sheet.write(index,7,str(p.max_buy))
				sheet.write(index,8,str(p.product.product.category.service.name).strip())
				sheet.write(index,9,str(p.product.product.category.parent.name).strip())
				sheet.write(index,10,str(p.product.product.category.name).strip())
				sheet.write(index,11,str('shubham.webfactional.com'+str(p.product.image)).strip())
				sheet.write(index,12,str(my_unicode(p.product.product.description)).strip())
				index+=1
				# print index
book.save('app/static/dump/all_products_on_server.xls')
