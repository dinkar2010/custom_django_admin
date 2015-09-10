import os
import urllib
from PIL import Image
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

def resize(path, size):
	NEWIMAGESIZE = 300
	if size=='xxs':
		NEWIMAGESIZE=50
	elif size=='xs':
		NEWIMAGESIZE = 100
	elif size=='s':
		NEWIMAGESIZE = 200
	elif size=='m':
		NEWIMAGESIZE = 300
	inFile = Image.open(path)
	outFile = path
	print "Origonal size ",inFile.size
	xDim = inFile.size[0]
	yDim = inFile.size[1]
	newSize = aspectRatio(xDim, yDim,NEWIMAGESIZE)
	print "new size ",newSize
	inFile = inFile.resize((int(newSize[0]),int(newSize[1])),Image.ANTIALIAS)
	inFile.save(outFile,optimize=True,quality=95)
def aspectRatio(xDim, yDim,NEWIMAGESIZE):

    if xDim <= NEWIMAGESIZE and yDim <= NEWIMAGESIZE: #ensures images already correct size are not enlarged.
        return(xDim, yDim)

    elif xDim > yDim:
        divider = xDim/float(NEWIMAGESIZE)
        xDim = float(xDim/divider)
        yDim = float(yDim/divider)
        return(xDim, yDim)

    elif yDim > xDim:
        divider = yDim/float(NEWIMAGESIZE)
        xDim = float(xDim/divider)
        yDim = float(yDim/divider)
        return(xDim, yDim)

    elif xDim == yDim:
        xDim = NEWIMAGESIZE
        yDim = NEWIMAGESIZE
        return(xDim, yDim)
