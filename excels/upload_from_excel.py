import xlrd
from app.models import *
from app.utils.image_utils import *


def save_products(start_row_no=1):
    workbook = xlrd.open_workbook('excels/Master Store Inventory.xlsx')
    store = Store.objects.get(pk=119)
    service=Service.objects.get(pk=2)
    worksheets = workbook.sheet_names()
    input_service = raw_input("Enter the Service: ")
    for worksheet_name in worksheets:
        worksheet=workbook.sheet_by_name(worksheet_name)
        print worksheet_name
        index = 1
        if worksheet_name==input_service : # or worksheet_name=="Groceries":
            num_rows = worksheet.nrows
            for i in range(num_rows+1)[start_row_no:]:
                print i
                try:
                    id = str(worksheet.cell_value(i,0)).strip()
                    is_basic = str(worksheet.cell_value(i,1)).strip()
                    brand_name = str(worksheet.cell_value(i,2)).strip()
                    if not brand_name:
                        brand_name="MVC"
                    name = str(worksheet.cell_value(i,3)).strip()
                    magnitude = float(str(worksheet.cell_value(i,4)).strip())
                    unit = str(worksheet.cell_value(i,5)).strip()
                    size_desc = str(worksheet.cell_value(i,6)).strip()
                    mrp = float(str(worksheet.cell_value(i,7)).strip())
                    if mrp==0:
			mrp=1
		    if is_basic:
                        is_basic=True
                    else:
                        is_basic=False
                    try:
                        store_price = float(str(worksheet.cell_value(i,8)).strip())
                    except:
                        print "not found store price "+name
                        store_price = mrp

                    try:
                        discount = float(str(worksheet.cell_value(i,9)).strip())
                    except:
                        discount=0

                    try:
                        max_buy_count = float(str(worksheet.cell_value(i,10)).strip())
                    except:
                        max_buy_count=20

                    category = str(worksheet.cell_value(i,11)).strip()
                    sub_category = str(worksheet.cell_value(i,12)).strip()
                    sub_sub_category = str(worksheet.cell_value(i,13)).strip()
                    image = str(worksheet.cell_value(i,14)).strip()

                    try:
                        status = str(int(float(str(worksheet.cell_value(i,15)).strip())))
                    except:
                        status = '1'

                    if status == '0':
                        status = False
                    else:
                        status = True
                    if status:
                        cat = Category.objects.filter(name__icontains=category)

                        if cat:
                           cat = cat[0]
                        else:
                            cat = Category(name=category,service =service)
                            cat.save()

                        sub_cat = Category.objects.filter(name__icontains=sub_category,parent=cat,service=service)

                        if sub_cat:
                            sub_cat = sub_cat[0]
                        else:
                            sub_cat = Category(name=sub_category,parent=cat,service=service)
                            sub_cat.save()

                        sub_sub_cat = None
                        if sub_sub_category:
                            sub_sub_cat=SubSubCategory.objects.filter(name__icontains=sub_sub_category,sub_category=sub_cat)

                        if sub_sub_cat:
                            sub_sub_cat = sub_sub_cat[0]
                        else:
                            sub_sub_cat = SubSubCategory(name=sub_sub_category,sub_category=sub_cat)
                            sub_sub_cat.save()

                        prd = Product.objects.filter(name=name,brand_name=brand_name,category=sub_cat)
                        if prd:
                            prd = prd[0]
                        else:
                            prd = Product(name=name,brand_name=brand_name,category=sub_cat,sub_sub_category=sub_sub_cat)
                            prd.save()

                        size = Size.objects.filter(magnitude=magnitude,unit=unit,description=size_desc)
                        if size:
                            size=size[0]
                        else:
                            size=Size(magnitude=magnitude,unit=unit,description=size_desc)
                            size.save()
                        isServer = settings.IS_SERVER
                        if isServer == 0:
                            path1 = '/home/shubham/webapps/movincart/app/static/productImage/'
                        else:
                            path1 = 'app/static/productImage/'

                        psi = ProductSizeImageMapping.objects.filter(product=prd, size=size)
                        if psi:
                            psi = psi[0]
                        else:
                            psi = ProductSizeImageMapping(product=prd, size=size, image='/static/no_image.jpg',is_basic_product=is_basic)
                            psi.save()
                            product_id = str(psi.id)
                            if image:
                                try:
                                    if '.png' in image:
                                        newpath = path1 + str(product_id) + '/s/'
                                        if not os.path.exists(newpath):
                                            os.makedirs(newpath)
                                        urllib.urlretrieve(image, newpath + 'item.png')
                                        resize(newpath + 'item.png', 's')
                                        newpath = path1 + str(product_id) + '/xs/'
                                        if not os.path.exists(newpath):
                                            os.makedirs(newpath)
                                        urllib.urlretrieve(image, newpath + 'item.png')
                                        resize(newpath + 'item.png', 'xs')
                                        newpath = path1 + str(product_id) + '/xxs/'
                                        if not os.path.exists(newpath):
                                            os.makedirs(newpath)
                                        urllib.urlretrieve(image, newpath + 'item.png')
                                        resize(newpath + 'item.png', 'xxs')
                                        newpath = path1 + str(product_id) + '/m/'
                                        if not os.path.exists(newpath):
                                            os.makedirs(newpath)
                                        urllib.urlretrieve(image, newpath + 'item.png')
                                        resize(newpath + 'item.png', 'm')
                                        newpath = '/static/productImage/' + str(product_id) + '/m/'
                                        image = newpath + 'item.png'
                                        psi.image = image
                                        print image
                                        print psi.id
                                        psi.save()
                                    else:
                                        newpath = path1 + str(product_id) + '/s/'
                                        if not os.path.exists(newpath):
                                            os.makedirs(newpath)
                                        urllib.urlretrieve(image, newpath + 'item.jpg')
                                        resize(newpath + 'item.jpg', 's')
                                        newpath = path1 + str(product_id) + '/xs/'
                                        if not os.path.exists(newpath):
                                            os.makedirs(newpath)
                                        urllib.urlretrieve(image, newpath + 'item.jpg')
                                        resize(newpath + 'item.jpg', 'xs')
                                        newpath = path1 + str(product_id) + '/xxs/'
                                        if not os.path.exists(newpath):
                                            os.makedirs(newpath)
                                        urllib.urlretrieve(image, newpath + 'item.jpg')
                                        resize(newpath + 'item.jpg', 'xxs')
                                        newpath = path1 + str(product_id) + '/m/'
                                        if not os.path.exists(newpath):
                                            os.makedirs(newpath)
                                        urllib.urlretrieve(image, newpath + 'item.jpg')
                                        resize(newpath + 'item.jpg', 'm')
                                        newpath = '/static/productImage/' + str(product_id) + '/m/'
                                        image = newpath + 'item.jpg'
                                        psi.image = image
                                        print image
                                        print psi.id
                                        psi.save()
                                except:
                                    pass
                        sp = StoreProductMapping.objects.filter(product=psi,store=store)
                        if not sp :
                            stock =False
                            if 'item' in str(psi.image):
                                stock=True
                            StoreProductMapping(store=store,product=psi,price=mrp,price_to_movincart=store_price,discount=discount,max_buy=max_buy_count,stock=stock).save()

                except Exception as e:
                    print '------------------------------------------------------------------------------------------------------------------------'
                    print '------------------------------------------------------------------------------------------------------------------------'
                    print "error in row = "+str(i)+" "+str(e)
                    pass

# save_products(start_row_no=1)
def upload_in_store(sheet=9):

    if sheet==0:
        workbook = xlrd.open_workbook('excels/groly.xlsx')
        store = Store.objects.get(pk=124)
    elif sheet==1:
        workbook = xlrd.open_workbook('excels/pareys.xlsx')
        store = Store.objects.get(pk=121)
    if sheet < 2:
        log = ""
        data=[]

        sheet = workbook.sheet_by_index(0)
        index=0

        for sp in store.storeproductmapping_set.all():
            sp.stock = False
            sp.save()

        for i in range(sheet.nrows - 1):

            id = sheet.cell_value(i+1, 0)
            name = sheet.cell_value(i+1, 4)
            mrp = sheet.cell_value(i+1, 6)
            store_price = sheet.cell_value(i+1, 7)
            discount = sheet.cell_value(i+1, 8)
            status = sheet.cell_value(i+1, 9)
            max_buy = sheet.cell_value(i+1, 10)
            to_be_saved = sheet.cell_value(i+1, 17)
            try:
                if "in" in status.lower():
                    status = True
                else:
                    status = False
                if not store_price:
                    store_price = mrp

                if to_be_saved:
                    prdsize = ProductSizeImageMapping.objects.get(pk=id)
                    store_product = StoreProductMapping.objects.filter(product=prdsize,store=store)
                    if store_product:
                        store_product = store_product[0]
                        log = "Product Already Exists"
                        store_product.price = mrp
                        store_product.price_to_movincart = store_price
                        store_product.discount = discount
                        store_product.stock = True
                        store_product.max_buy = max_buy
                    else:
                        store_product = StoreProductMapping(product=prdsize,store=store,stock=True,price=mrp,price_to_movincart=store_price,discount=discount,max_buy=max_buy)
                        log = "New Product Added"
                    store_product.save()
                    index+=1
            except Exception as e:
                print "Error : "+str(e)
                index+=1
                pass

        data = simplejson.dumps({'data':data})
upload_in_store(sheet=1)
