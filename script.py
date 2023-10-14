import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os
import re
import time


def getProductInfo(url):
    with webdriver.Chrome(service=Service(ChromeDriverManager().install())) as driver:  # Открываем хром
        driver.get(url)  # Открываем страницу
        time.sleep(3)  # Время на прогрузку страницы
        soup = BeautifulSoup(driver.page_source, 'html.parser')

    product_information = []
    product_information.append(getProductArticle(soup))
    product_information.append(getProductName(soup))
    product_information.append(url)
    product_information.append(getRegularPrice(soup))
    product_information.append(getPromoPrice(soup))
    product_information.append(getBrand(soup))
    return product_information

def getProductArticle(soup):
    try:
        article = soup.select('.product-page-content__article')
        return int(re.findall("\d+", (article[0].text).replace('  ', '').replace('\n', '').replace("\xa0", ''))[0])
    except:
        print("error getting article")
        return "error"

def getProductName(soup):
    try:
        name = soup.select('.heading__h2')
        return str((name[0].text).replace('  ', '').replace('\n', '').replace("\xa0", ''))
    except:
        print("error getting name!!!")
        return "error"

def getRegularPrice(soup):
    try:
        return int(soup.select('.product-price__sum-rubles')[0].text.replace("\xa0", ''))
    except:
        print("error getting regprice!!!")
        return "error"

def getPromoPrice(soup):
    try:
        if len(list(soup.select('.product-page-content__price-validity'))) == 0:
            return int(soup.select('.product-price__sum-rubles')[0].text.replace("\xa0", ''))
        else:
            return int(soup.select('.product-price__sum-rubles')[1].text.replace("\xa0", ''))
    except:
        print("error getting promprice!!!")
        return "error"

def getBrand(soup):
    try:
        return str(soup.select('.product-attributes__list-item')[0].text.replace('  ', '').replace('\n', '').replace("\xa0", '').replace('Бренд', ''))
    except:
        print("error getting brand!!!")
        return "error"


def getAllUrls():
    list_of_pages = [] # Делаем список ссылок на все позиции

    ##Первую страницу отдельно забираем

    url = f"https://online.metro-cc.ru/category/chaj-kofe-kakao/chay?in_stock=1"
    parsed_url = urlparse(url)
    domain = parsed_url.scheme + '://' + parsed_url.netloc
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    for link in soup.find_all('a', href=True):
        full_url = urljoin(domain, link['href'])
        if full_url not in links:
            links.append(full_url)
    page_links = []
    page_links = links[links.index('https://rioba.metro-cc.ru?erid=LatgBvBmv') + 1: links.index(
        f'https://online.metro-cc.ru/category/chaj-kofe-kakao/chay?in_stock=1')]
    list_of_pages.append(page_links)

    for page in range(2, 10):
        url = f"https://online.metro-cc.ru/category/chaj-kofe-kakao/chay?page={page}&in_stock=1"
        parsed_url = urlparse(url)
        domain = parsed_url.scheme + '://' + parsed_url.netloc
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = []
        for link in soup.find_all('a', href=True):
            full_url = urljoin(domain, link['href'])
            if full_url not in links:
                links.append(full_url)
        page_links = []
        page_links = links[links.index('https://rioba.metro-cc.ru?erid=LatgBvBmv') + 1: links.index(
            f'https://online.metro-cc.ru/category/chaj-kofe-kakao/chay?page={page - 1}&in_stock=1')]
        list_of_pages.append(page_links)
    return list_of_pages


def parseTea():
    links = getAllUrls()
    dict_links = {}
    dict_links = dict(enumerate(links, start=1))
    information_list = []
    for key in dict_links.keys():
        for elem in dict_links[key]:
            print(elem)
            info = getProductInfo(elem)
            information_list.append(info)
            print(info)

    return information_list


def createExcel(information):
    d1 = {}
    d1["id товара"], d1["Наименование"], d1["Ссылка"], d1["Цена без скидки"], d1["Цена со скидкой"], d1[
        "Бренд"] = [], [], [], [], [], []
    for elem in information:
        d1["id товара"].append(elem[0])
        d1["Наименование"].append(elem[1])
        d1["Ссылка"].append(elem[2])
        d1["Цена без скидки"].append(elem[3])
        d1["Цена со скидкой"].append(elem[4])
        d1["Бренд"].append(elem[5])
    df = pd.DataFrame(d1)
    df.to_excel("tea.xlsx", sheet_name="tea")




