import erniebot
import os
from dotenv import load_dotenv
from ._PROMPT import *
from .web_search import Bing_search
from .chroma_search import search_chroma
from .mysql_db import *
import json
import time
import random
import pymysql
load_dotenv()
Bing_Search = Bing_search(subscription_key = os.getenv("AZURE_SEARCH_API_KEY"))


config = {
    'host': os.getenv("MYSQL_HOST"),
    'user': os.getenv("MYSQL_USER"),
    'password': os.getenv("MYSQL_PASSWORD"),
    'db': os.getenv("MYSQL_DB")
}

def extract_and_parse_json(text):
    # 查找第一个左花括号
    start_index = text.find('{')
    # 查找第一个右花括号
    end_index = text.rfind('}')
    
    # 如果没有找到花括号，返回None
    if start_index == -1 or end_index == -1:
        return None
    
    # 提取花括号内的字符串
    json_str = text[start_index:end_index+1]
    
    try:
        # 尝试解析JSON字符串
        data = json.loads(json_str)
        return data
    except json.JSONDecodeError as e:
        # 如果解析出错，返回错误信息
        return {"json解析出错":e}
    


class Law_Work():
    ACCESS_TOKEN = os.getenv("BAIDU_API_KEY")
    
    def __init__(self,access_token, model :str = "ernie-4.0", ) -> None:
        
        erniebot.api_type = os.getenv("BAIDU_API_TYPE")

        erniebot.access_token = access_token
        self.model = model
        self.db_connection = pymysql.connect(**config)

    def generate_unique_id_with_datetime(self):
        current_datetime = time.strftime("%Y%m%d%H%M%S")  # 获取当前日期时间(年月日时分秒格式)
        random_number = random.randint(1, 1000)  # 生成一个随机数

        unique_id = int(f"{current_datetime}{random_number:03}")
        
        return unique_id
        

    def first_chat(self, question: str):
        messages = [
        # {
        #     "role": "system",
        #     "content": FIRST_SYSTEM_PROMPT
        # },
        {
            "role": "user",
            "content": FIRST_USER_PROMPT.format(question = question)
        }]
        response = erniebot.ChatCompletion.create(
            model = self.model,
            messages = messages
        )
        return response["result"]
    def other_chat(self, question: str):
        messages = [
        # {
        #     "role": "system",
        #     "content": OTHER_SYSTEM_PROMPT
        # },
        {
            "role": "user",
            "content": OTHER_USER_PROMPT.format(question = question)
        }]
        response = erniebot.ChatCompletion.create(
            model = self.model,
            messages = messages,
            stream = True
        )
        return response
    def web_search_data(self, question: str, count :int = 6):
        search_data = Bing_Search.get_search(question = question, count = count)
        res = ""
        for i in search_data[0]:
            res = res + i + "\n"
        return res,search_data
    
    def chroma_db_data(self, question: str, count :int = 6):
        db_data = search_chroma(query_texts = question, n_results = count)
        res = ""
        for i in db_data:
            res = res + i + "\n"
        return res

    def law_chat(self, question: str, ):

        search_content = self.web_search_data(question = question)
        law_content = self.chroma_db_data(question = question)
        messages = [
        # {
        #     "role": "system",
        #     "content": LAW_SYSTEM_PROMPT
        # },
        {
            "role": "user",
            "content": LAW_USER_PROMPT.format(question = question, search_content = search_content[0], law_content = law_content)
        }]
        response = erniebot.ChatCompletion.create(
            model = self.model,
            messages = messages,
            stream = True
        )
        return response,search_content[1],law_content

    def handle_other_chat(self, question_id, question):
        other_answer = self.other_chat(question=question)
        update_other_chat(self.db_connection, question_id=question_id, other_chat=other_answer)
        return other_answer, (), question_id
    
    def run(self, question: str):
        question_id = self.generate_unique_id_with_datetime()
        first_answer = self.first_chat(question=question)
        insert_id_first_chat(self.db_connection, question_id=question_id,question = question, first_chat=str(first_answer))
        
        # 尝试提取问题类型并基于结果调用相应的方法
        try:
            question_type = extract_and_parse_json(first_answer)
            print(question_type)
            print(type(question_type))

            if isinstance(question_type, dict):
                if question_type.get("law_question"):
                    law_chat_data = self.law_chat(question=question)
                    answer, search_data, law_data = law_chat_data
                    update_web_law_search(self.db_connection, question_id=question_id, web_search=str(search_data), law_search=str(law_data))
                    return answer, search_data, question_id
                else:
                    return self.handle_other_chat(question_id, question)
            else:
                return self.handle_other_chat(question_id, question)
        except Exception as e:
            # 在异常情况下也处理为其他类型的对话
            return self.handle_other_chat(question_id, question)
            # print(e)

        

# test

# test = Law_Work(model="ernie-3.5")
# res = test.other_chat("如何支付加班费")
# # print(res[1])
# result = ""
# for resp in res:
#     print(resp)
#     result += resp.get_result()
#     break
# print(result)

# response = erniebot.ChatCompletion.create(
#     model='ernie-3.5',
#     messages=[{
#         'role': 'user',
#         'content': "请问你是谁？"
#     }],)

# print(response.get_result())

# web_search




