from app.models import *

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

ppp = Product.objects.all()
for p in ppp:
	p.name = str(my_unicode(p.name))
	p.brand_name = str(my_unicode(p.brand_name))
	p.save()