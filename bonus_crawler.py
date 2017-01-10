from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from io import StringIO

class BonusCrawler:
  '''
  This AH bonus crawler extracts the information of products on sale from AH website.  
  '''
  #store all urls crawled
  urls_all = []
  #store urls to be crawled
  urls = []
  #store all products crawled
  products = {}

  def __init__(self, first_url, webdriver_path):
    self.urls.append(first_url)
    self.urls_all.append(first_url)
    self.driver = webdriver.Chrome(webdriver_path)

  #get product info at the current page
  def getprodinfo(self, url):
    try:
      self.driver.get(url)
      WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.XPATH, '//body/div/div/div/div/article[last()]')))      
      
      #get html
      element = self.driver.find_element_by_xpath('//*')
      html = element.get_attribute('outerHTML') 
       
      #parse html and find elements  
      parser = etree.HTMLParser()
      self.html_tree = etree.parse(StringIO(html), parser)
      li = self.html_tree.xpath('//div/div/div/div/article')
      
      for prod in li:
        p = prod.find('./a')
        if p is not None:
          name = p.find('./div/h1').text
          if name not in self.products:
            product = {}
            product['amount'] = p.find('./div[1]/span').text
            before = p.find('./div[3]/div[1]/span')
            after = p.find('./div[3]/div[2]/span')
            if before is not None and after is not None and after.text != '.':
              product['price_before'] = before.text
              product['price_after'] = after.text
            else:
              product['price_before'] = None
              product['price_after'] = None	
            product['discount'] = p.find('./div[2]/span').text
            self.products[name] = product
    
    except Exception as e:
      print ('An error occured: {0}'.format(e))
    
    return self.products

  #keep crawling sub-pages
  def crawl(self):
    urls_temp = []
    for url in self.urls:
      self.getprodinfo(url)
      urls_to_be_extracted = []

      #navigate to the element including further url paths
      li = self.html_tree.xpath('//div/div/div/div/article/div/a')
      urls_to_be_extracted = ['https://www.ah.nl' + ele.attrib['href'] for ele in li]
      urls_temp = urls_to_be_extracted
      self.urls = urls_temp
      self.urls_all.extend(urls_temp)

    #crawl more or terminate
    if not urls_temp:
      self.driver.quit()
      return self.urls_all
    else:
      self.crawl()


ah_url = 'https://www.ah.nl/bonus'
chrome_driver = input("Please enter the path of your chrome webdriver:")
bonus_crawler = BonusCrawler(ah_url, chrome_driver)
bonus_crawler.crawl()
