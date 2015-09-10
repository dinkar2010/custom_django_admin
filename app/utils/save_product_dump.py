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
def save_dump(stores):
    products =StoreProductMapping.objects.filter(store__id__in=stores)
    book = xlwt.Workbook()
    sheet = book.add_sheet("Sheet1", cell_overwrite_ok=True)
    index=1
    sheet.write(0,0,'ID')
    sheet.write(0,1,'Basic/Non-Basic')
    sheet.write(0,2,'Store')
    sheet.write(0,3,'Brand name')
    sheet.write(0,4,'Name')
    sheet.write(0,5,'Size')
    sheet.write(0,6,'MRP')
    sheet.write(0,7,'Store Price')
    sheet.write(0,8,'Discount')
    sheet.write(0,9,'Status')
    sheet.write(0,10,'Max Buy Quantity')
    sheet.write(0,11,'Service')
    sheet.write(0,12,'Category')
    sheet.write(0,13,'Sub-Category')
    sheet.write(0,14,'Sub-Sub-Category')
    sheet.write(0,15,'Image')
    sheet.write(0,16,'About')

    for p in products:
        sheet.write(index,0,str(p.product.id))
        is_basic = "Non Basic"
        if p.product.is_basic_product:
            is_basic = "Basic"
        sheet.write(index,1,str(is_basic))
        sheet.write(index,2,str(p.store.name))
        sheet.write(index,3,str(my_unicode(p.product.product.brand_name)))
        sheet.write(index,4,str(my_unicode(p.product.product.name)))
        sheet.write(index,5,str(p.product.size.magnitude)+" "+str(p.product.size.unit)+" "+str(p.product.size.description))
        sheet.write(index,6,str(p.price))
        sheet.write(index,7,str(p.price_to_movincart))
        sheet.write(index,8,str(p.discount))
        if p.stock:
            status="In Stock"
        else:
            status="Out of Stock"
        sheet.write(index,9,status)
        sheet.write(index,10,str(p.max_buy))
        sheet.write(index,11,str(p.product.product.category.service.name).strip())
        sheet.write(index,12,str(p.product.product.category.parent.name).strip())
        sheet.write(index,13,str(p.product.product.category.name).strip())
        ssc=""
        if p.product.product.sub_sub_category:
            ssc = p.product.product.sub_sub_category.name
        sheet.write(index,14,str(ssc))
        sheet.write(index,15,str('http://shubham.webfactional.com'+str(p.product.image)).strip())
        sheet.write(index,16,str(my_unicode(p.product.product.description)).strip())
        index+=1
                    # print index
    isServer =settings.IS_SERVER
    path1=''
    if isServer==0:
        path1='/home/shubham/webapps/movincart/'
    book.save(path1+'dump/products_on_server.xls')
