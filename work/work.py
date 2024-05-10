import erniebot
import os
from dotenv import load_dotenv
from ._PROMPT import *
from .web_search import Bing_search
from .chroma_search import search_chroma
import json

load_dotenv()
Bing_Search = Bing_search(subscription_key = os.getenv("AZURE_SEARCH_API_KEY"))


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
        return f"JSON解析错误: {e}"

class Law_Work():
    ACCESS_TOKEN = os.getenv("BAIDU_API_KEY")
    
    def __init__(self,access_token, model :str = "ernie-4.0", ) -> None:
        
        erniebot.api_type = os.getenv("BAIDU_API_TYPE")

        erniebot.access_token = access_token
        self.model = model
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
        return response,search_content[1]

    def run(self, question: str):
        question_type = extract_and_parse_json(self.first_chat(question = question))
        try:    
            if "law_question" in question_type:
                if question_type["law_question"] == True:
                    law_chat_data = self.law_chat(question = question)
                    answer = law_chat_data[0]
                    search_data = law_chat_data[1]
                    return answer,search_data
                else:
                    return self.other_chat(question = question),()
            else:
                return self.other_chat(question = question),()
        except Exception as e:
            return "抱歉，我无法回答你的问题，请尝试其他问题。"

        

# test

# test = Law_Work(model="ernie-4.0")
# res = test.web_search_data("如何支付加班费")
# print(res[1])
# result = ""
# for resp in res:
#     result += resp.get_result()
# print(result)

# response = erniebot.ChatCompletion.create(
#     model='ernie-3.5',
#     messages=[{
#         'role': 'user',
#         'content': "请问你是谁？"
#     }],)

# print(response.get_result())

# web_search




