import cookielib,urllib,urllib2,httplib
import re
import StringIO
import seccode as sc

HEADERS = { 
		'Host':'obmem.com',
		'User-Agent':'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.2pre) Gecko/20100303 Ubuntu/9.10 (karmic) Namoroka/3.6.2pre',
		'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		'Accept-Language':'en-us,en;q=0.5',
		'Accept-Charset':'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
		'Keep-Alive':'115',
		'Connection':'keep-alive',
		'Referer':'http://obmem.com/crackdz/register.php'
	}

def checkusername(username):
	url = 'http://obmem.com/crackdz/ajax.php?infloat=register&handlekey=register&action=checkusername&username='+username+'&inajax=1&ajaxtarget=returnmessage4'
	req = urllib2.Request( url=url, headers=HEADERS )
	return urllib2.urlopen(req).read()

def checkemail(email):
	url = 'http://obmem.com/crackdz/ajax.php?infloat=register&handlekey=register&action=checkemail&email='+email+'&inajax=1&ajaxtarget=returnmessage4'
	req = urllib2.Request( url=url, headers=HEADERS )
	return urllib2.urlopen(req).read()

def getseccode():
	print '...getting seccode'
	url = 'http://obmem.com/crackdz/ajax.php?action=updateseccode&inajax=1&ajaxtarget=seccodeverify_register_menu_content'
	req = urllib2.Request( url=url, headers=HEADERS )
	secxml = urllib2.urlopen(req).read()

	securl = 'http://obmem.com/crackdz/'+re.compile(r'src="(seccode\.php.*?)"').search(secxml).group(1)
	req = urllib2.Request( url=securl, headers=HEADERS )
	return urllib2.urlopen(req).read()
	

def solveseccode(seccode):
	sc.loadsamples()
	im = sc.getframe( StringIO.StringIO(seccode) )
	return sc.crackcode(im)

def checkseccode(seccodeverify):
	if seccodeverify == 'failed':
		return False
	print '...checking seccode '+seccodeverify
	url = 'http://obmem.com/crackdz/ajax.php?inajax=1&action=checkseccode&seccodeverify='+seccodeverify
	req = urllib2.Request( url = url, headers = HEADERS )
	checkreturn = urllib2.urlopen(req).read()
	found = re.compile('succeed').search(checkreturn)
	if found:
		return True
	else:
		return False
	
def regsubmit( tp ):
	(formhash,username,password,email,seccodeverify) = tp
	regurl = 'http://obmem.com/crackdz/register.php?regsubmit=yes&inajax=1'
	postdata = urllib.urlencode({
		'formhash':formhash,
		'referer':'',
		'activationauth':'',
		'username':username,
		'password':password,
		'password2':password,
		'email':email,
		'seccodeverify':seccodeverify,
		'field_1new':'1',
	})
	req = urllib2.Request( url = regurl, data=postdata )
#	req.add_header('User-Agent','Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.2pre) Gecko/20100303 Ubuntu/9.10 (karmic) Namoroka/3.6.2pre')
	req.add_header('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
	req.add_header('Accept-Language','en-us,en;q=0.5')
	req.add_header('Accept-Charset','ISO-8859-1,utf-8;q=0.7,*;q=0.7')
	req.add_header('Referer','http://obmem.com/crackdz/register.php')

	rtn = urllib2.urlopen(req).read()
	if 'register_succeed' in rtn:
		return 'register_succeed'
	else:
		return rtn
	

def register(username,password,email):
	cookie=cookielib.CookieJar()
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie), urllib2.HTTPHandler)
	urllib2.install_opener(opener)
	
	regpage = urllib2.urlopen('http://obmem.com/crackdz/register.php').read()
	formhash = re.compile(r'name="formhash" value="(.*?)"').search(regpage).group(1)

	checkusername(username)
	checkemail(email)

	seccode = getseccode()

#	open('sec.gif','wb').write(seccode)
#	mycode = raw_input()

	seccodeverify = solveseccode(seccode)
	seccodeverify = seccodeverify[:10]
	i = 0
	while i<len(seccodeverify) and not checkseccode(seccodeverify[i]):
		i += 1
	while i == len(seccodeverify):
		seccode = getseccode()
		seccodeverify = solveseccode(seccode)
		i = 0
		while i<len(seccodeverify) and not checkseccode(seccodeverify[i]):
			i += 1
	
	rtn = regsubmit( (formhash,username,password,email,seccodeverify[i]) )
#	rtn = regsubmit( (formhash,username,password,email,mycode) )
	return rtn

def gentest():
	for i in range(1,121):
		print i
		r  = getseccode()
		open('test/%03d.gif'%i,'w').write(r)
	exit(1)
	for i in range(10000):
		print i
		rtn = register('testrobot%04d'%i,'test123','testrobot%04d@163.com'%i)
		print rtn

if __name__ == '__main__':
	for i in range(100,200):
		print i
		name = 'test1%05d'%i
		email = name+'@163.com'
		register(name,'test123',email)
