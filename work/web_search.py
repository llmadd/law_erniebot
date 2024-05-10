import os
import re
import time
from typing import List,Optional,Union,Dict,Any
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
load_dotenv()

def find_punctuation_start_end(text, punctuations=["。","，","！","？",".","?","!"]):
    # 将标点符号列表转换为正则表达式的形式
    pattern = "[" + re.escape("".join(punctuations)) + "]"
    
    # 使用正则表达式查找第一个匹配的标点符号
    first_match = re.search(pattern, text)
    first_position = first_match.start() if first_match else 0
    # print(first_match)
    # 使用正则表达式查找最后一个匹配的标点符号
    last_match = re.search(pattern + ".*$", text)
    last_position = last_match.end() if last_match else -1
    # print(last_match)
    return first_position, last_position

####################
#### BingSearch ####
####################

class BingCustomSearch_tool():

    def __init__(self, subscriptionKey: str, customConfigId:str) -> None:
        # self.question = question
        self.subscriptionKey = subscriptionKey
        self.customConfigId = customConfigId
    
    def get_search(self,question,count:int = 5):

        url = 'https://api.bing.microsoft.com/v7.0/custom/search?' + 'customconfig=' + self.customConfigId
        params = {
            "q": question,
            "count": count,
            "textDecorations": True,
            "textFormat": "HTML",
            "mkt": "en-US",
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Ocp-Apim-Subscription-Key': self.subscriptionKey
        }
        r = requests.get(url, headers=headers,params=params,timeout=50000)
        r.raise_for_status()

        search_results = r.json()
        print(search_results)
        load_search_data = []
        load_search_url = []
        if "webPages" in search_results:
            for item in search_results["webPages"]["value"]:
                url= item["url"]
                snippet = item["snippet"]
                # 正则表达式去除Html标签
                snippet = re.sub('<.*?>', '', snippet)
                load_search_data.append(snippet)
                load_search_url.append(url)
            return load_search_data,load_search_url
        else:
            search_res = " "
            return search_res
    
    def url_data(self,url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # 这会抛出异常如果请求失败
            content = response.content.decode('utf-8')

            soup = BeautifulSoup(content, 'html.parser')

            # 这里选择了多个可能包含文本的标签
            text_tags = ['div', 'p', 'span', 'article', 'li', 'td', 'section','h1',"a"]
            page_data = []

            for tag in text_tags:
                elements = soup.find_all(tag)
                for element in elements:
                    # 如果元素内部还包含其他的标签，那么就跳过这个元素
                    if any(element.find(child_tag) for child_tag in text_tags):
                        continue
                    # 获取元素的文本内容，并过滤掉空白符与不必要的空格
                    text = element.get_text(separator=' ', strip=True)
                    if text:
                        page_data.append(text)
            # 清理文本
            page_text = ' '.join(page_data)
            page_text = re.sub(r'\s+', ' ', page_text)  # 把多余的空白字符变成一个空格
            if page_text.__len__()<50:
                page_text = ''
        except requests.HTTPError as e:
            print(f"HTTP Error: {e}")
            page_text = ''
        except requests.RequestException as e:
            print(f"Request Exception: {e}")
            page_text = ''
        except Exception as e:
            print(f"Other Exception: {e}")
            page_text = ''

        return page_text
    
    def run(self,question):
        get_result = self.get_search(question)
        if type(get_result) != tuple:
            return get_result
        else:
            snippet,url = get_result
            for url_iteam in url:    
                url_data = self.url_data(url_iteam)
                if url_data != '':
                    break
            return url,snippet,url_data

        

#############
### TEST ####
#############
# CST = BingCustomSearch_tool(subscriptionKey="",customConfigId = "")
# res = CST.run('如何用python写一个爬虫') 
# print(res)

class Bing_search():
    def __init__(self,subscription_key: str):
        self.subscription_key = subscription_key
        self.search_url = "https://api.bing.microsoft.com/v7.0/search"
    
    def get_search(self,question,count:int = 5):

        url = self.search_url
        params = {
            "q": question,
            "count": count,
            "textDecorations": True,
            "textFormat": "HTML",
            "mkt": "en-US",
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Ocp-Apim-Subscription-Key': self.subscription_key
        }
        r = requests.get(url, headers=headers,params=params,timeout=50000)
        r.raise_for_status()
        search_results = r.json()
        load_search_data = []
        load_search_url = []

        if "webPages" in search_results:
            for item in search_results["webPages"]["value"]:
                url= item["url"]
                snippet = item["snippet"]
                # 正则表达式去除Html标签
                snippet = re.sub('<.*?>', '', snippet)
                load_search_data.append(snippet)
                load_search_url.append(url)
            return load_search_data,load_search_url
        else:
            search_res = " "
            return search_res
        
    def url_data(self,url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
        }

        try:
            response = requests.get(url, headers=headers)
            # content = response.content.decode('utf-8')
            response.raise_for_status()  # 这会抛出异常如果请求失败
            content = response.content.decode('utf-8')

            soup = BeautifulSoup(content, 'html.parser')

            # 这里选择了多个可能包含文本的标签
            text_tags = ['div', 'p', 'span', 'article', 'li', 'td', 'section','h1',"a"]
            page_data = []

            for tag in text_tags:
                elements = soup.find_all(tag)
                for element in elements:
                    # 如果元素内部还包含其他的标签，那么就跳过这个元素
                    if element.find(text_tags):
                        continue
                    # 获取元素的文本内容，并过滤掉空白符与不必要的空格
                    text = element.get_text(separator=' ', strip=True)
                    if text:
                        page_data.append(text)

            # 清理文本
            page_text = ' '.join(page_data)
            page_text = re.sub(r'\s+', ' ', page_text)  # 把多余的空白字符变成一个空格
            # print(len(page_text))
            star,end = find_punctuation_start_end(page_text)
            page_text = page_text[star+1:end]
            if len(page_text) < 50:
                page_text = ''
        except requests.HTTPError as e:
            print(f"HTTP Error: {e}")
            page_text = ''
        except requests.RequestException as e:
            print(f"Request Exception: {e}")
            page_text = ''
        except Exception as e:
            print(f"Other Exception: {e}")
            page_text = ''

        return page_text
    
    def run(self,question):
        get_result = self.get_search(question)
        if type(get_result) != tuple:
            return get_result
        else:
            snippet,url = get_result
            for url_iteam in url:    
                url_data = self.url_data(url_iteam)
                if url_data != '':
                    break
            return url,snippet,url_data






#############
### TEST ####
#############
# s = time.time()
# BS = Bing_search(subscription_key = "")
# res = BS.run("如何支付加班费")
# print(res[2])
# e = time.time()
# print(e-s)
