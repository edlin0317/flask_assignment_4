from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
import json
import time
from bs4 import BeautifulSoup
import requests

def run():
	options = Options()
	options.add_argument('--disable-dev-shm-usage')#防止 ram 不夠 -> page crash
	driver = webdriver.Chrome('/app/.chromedriver/bin/chromedriver', options=options)
	
	url = 'https://tw.news.yahoo.com/world'
	driver.get(url)
	while True:
	    #紀錄下拉之前的 page_source 長度
	    old_length = len(driver.page_source)
	    #傳送 END 按鍵，拉至最底
	    body = driver.find_element_by_css_selector('body')
	    body.send_keys(Keys.END)
	    #等待載入
	    time.sleep(2)
	    #紀錄下拉之後的 page_source 長度
	    new_length = len(driver.page_source)
	    print('%s,%s,%.3f'%(new_length,old_length,new_length/old_length))
	    #比較下拉前與下拉後的 page_source 長度，差異小於 1% 則判斷為已拉至底部
	    if new_length/old_length < 1.01:
	        print('reached bottom')
	        break
	soup = BeautifulSoup(driver.page_source)
	#找到大圖
	large = soup(class_='Pos(r) D(ib) W(HeroStandardImageWidth) H(100%) C(#fff) Td(u):h')
	print(len(large))
	#找到中圖
	medium = soup(class_='Z(0) Pos(r) Fz(16px) H(192px)')
	print(len(medium))
	#找到小圖
	small = soup(class_='js-stream-content Pos(r)')
	print(len(small))

	result_url_list = []
	#紀錄大圖連結
	result_url_list.append(large[0].a['href'])
	#紀錄中圖連結
	for elem in medium:
	    result_url_list.append(elem.a['href'])
	#紀錄小圖連結
	for elem in small:
	    #忽略廣告連結
	    if '>廣告<' in str(elem):
	        continue
	    result_url_list.append(elem.a['href']) 
	print('總連結數 : %s 個'%len(result_url_list))

	#剔除不是新聞連結
	tmp = []
	for elem in result_url_list:
	    #忽略 Yahoo Games, Yahoo TV, Yahoo Movies連結
	    if ('games.yahoo' in elem) or ('tv.yahoo' in elem) or ('movies.yahoo' in elem):
	        continue
	    tmp.append(elem)
	result_url_list = tmp

	#總共蒐集到幾個連結
	print('可爬連結數 : %s 個'%len(result_url_list))

	driver.quit()
	#以下只用 requests
	result = []
	#前往每個連結
	for elem in result_url_list:
	    #補上完整連結
	    if elem[0] == '/':
	        elem = 'https://tw.news.yahoo.com' + elem
	    url = elem
	    while True:
	        try:
	            r = requests.get(url)
	            break
	        except:
	            time.sleep(2)
	    soup = BeautifulSoup(r.text)
	    #找到新聞標題
	    title = soup.find('h1').text
	    #找到第一個大圖連結
	    try:
	        yimg = soup.find(class_='caas-img-container').find('img')['src']
	    except:#找不到大圖
	        yimg = ""
	    #紀錄文章每個段落的文字
	    article = soup.find(class_='caas-body')
	    content = ""
	    for paragraph in article('p'):
	        #去除 「更多XX報導」段落
	        garbage = ['<span>更多', '更多鏡週刊', '看更多 CTWANT 文章', '更多中時', '更多 TVBS 報導', '更多相關新聞', '更多影劇新聞', '更多Movie訊息', '更多電影資訊', '更多精彩內容請至', '更多資訊請見', '更多華視', '更多CNEWS', '更多 NOWnews 今日新聞', '更多三立', '更多精彩報導', '更多生活相關新聞', '更多東森', '更多草根影響力', '更多影片請', '更多民視', '更多上報內容', '更多寵毛網']
	        found_garbage = False
	        #逐一比對該段落是否有以上文字
	        for gg in garbage:
	            #發現以上文字，跳出，不做紀錄
	            if gg in str(paragraph):
	                found_garbage = True
	                break
	        #發現以上文字，跳出，不做紀錄
	        if found_garbage:
	            break
	        content += paragraph.text+'\n'
	    print(title)
	#     print(url)
	#     print(yimg)
	#     print(content)
	    #紀錄結果
	    result.append(
	        {
	            'title':title,
	            'url':url,
	            'yimg':yimg,
	            'content':content
	        }
	    )
	#輸出至 json 檔
	with open('yahoo-news.json', 'w', encoding="utf-8") as f:
	    f.write(json.dumps(result, indent=2, ensure_ascii=False))

	result = 'https://linebot4106029040.herokuapp.com/getfile/yahoo-news.json'
	driver.quit()
	return result