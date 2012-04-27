import cookielib,urllib,urllib2,httplib
from BeautifulSoup import BeautifulSoup
import re
import StringIO
import seccode as sc

weburl="http://tieba.baidu.com"

HEADERS = { 
		'Host':'tieba.baidu.com',
		'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/533.4 (KHTML, like Gecko) Chrome/5.0.375.70 Safari/533.4',
		'Referer':'http://tieba.baidu.com/wow',
		'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		'Accept-Language':'zh-CN,zh;q=0.8',
		'Accept-Charset':'GBK,utf-8;q=0.7,*;q=0.3',
		'Keep-Alive':'115',
		'Connection':'keep-alive',
		'Referer':'http://tieba.baidu.com/tts',
		'Cookie':'BAIDUID=6E6CFDB5803FA00CE90E8C0575B66421:FG=1; TIEBAUID=69f9537a2138e2b9dcfeb3a0; TB_BAR_SIGNIN_GUIDE_NEW=1; _Mi=false_unknown; __utmz=147196964.1271296816.2.2.utmcsr=baidu.hexun.com|utmccn=(referral)|utmcmd=referral|utmcct=/stock/q.php; __utma=147196964.337335832.1271056700.1271056700.1271296816.2; TIEBAPB=NEWPB; BD_UTK_DVT=1; Hm_lpvt_eedec8cb8159470f2c25a22d1a9fef7c=1276066600039; Hm_lvt_eedec8cb8159470f2c25a22d1a9fef7c=1276066600039; USERID=8e7497720523be16449310; BDUSS=RJVUdsVlY2R0FCcE1QV3lmcXNGVW1EUGJPMUhuYmx1dnRaRURmUUpMenYxalpNQUFBQUFBJCQAAAAAAAAAAAoX94wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAChG0IAAAAAAAAAAAAAAAAAcNH6pCoAAAAAAAAAChfxa-9JD0zvSQ9MaE;TB_POST_SIGNIN_GUIDE=1'
	}

def submit():
	regurl = 'http://tieba.baidu.com/f?'
	postdata = urllib.urlencode({
		'ct':'385875968',
		'tn':'ajaxThreadSubmit',
		'word':'tts',
		#'username':'zihen01',
		#'password':'buguan3721',
		'captcha':'0',
		'ti':'biao ti yao chang!!',
		'textInput':'rt',
		'lm':'413366',
		'z':'0',
		'sc':'0',
		'cm':'0',
		'rn':'0',
		'bs':'',
		'str2':'0',
		'str3':'6E6CFDB5803FA00CE90E8C0575B66421',
		'str4':'823796883a5960a7',
		'str1':'',
		'rs4':'',
		'code':'1',
		'rs14':'0'
	})
	req = urllib2.Request( url = regurl, data=postdata )
	req.add_header('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
	req.add_header('Accept-Language','en-us,en;q=0.5')
	req.add_header('Accept-Charset','ISO-8859-1,utf-8;q=0.7,*;q=0.7')
	req.add_header('Referer','http://tieba.baidu.com/tts')
	rtn = urllib2.urlopen(req).read()
	print rtn
	
def getSingStr(regurl):
	#cookie = cookielib.CookieJar()
	#opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie)) 
	#urllib2.install_opener(opener)
	securl = regurl+'/f?ct=486539264&cm=59200&lm=73787&rs1=0&rs10=1&word=&tn=jsonVcode&t=0.41394683066755533'
	req = urllib2.Request( url=securl, headers=HEADERS )
	sign = urllib2.urlopen(req).read()
	return sign[15:-3]

def genCaptcha(sign):
	securl=weburl+'/cgi-bin/genimg?'+sign+'&t=0.6879592565819621'
	print securl
	#req = urllib2.Request(url=securl, headers=HEADERS )
	#print urllib2.urlopen(req).read()
	urllib.urlretrieve(securl, "sign.jpg")

def openUrl(url):
	req = urllib2.Request( url=url, headers=HEADERS )
	page = urllib2.urlopen(req)
	#soup = BeautifulSoup(page)
	#div_title = soup.findAll('a',href=re.compile('^.+?$'))
	#print div_title
	print soup.prettify()
	
if __name__ == '__main__':
	#openUrl('http://tieba.baidu.com/tts')
	#submit()
	signStr = getSingStr('http://tieba.baidu.com')
	genCaptcha(signStr)