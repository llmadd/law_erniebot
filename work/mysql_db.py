import pymysql



# def insert_data(id, question, answer, web_search, law_search):
#     sql = "INSERT INTO baidu_law (id, question, answer, web_search, law_search) VALUES (%d, %s, %s, %s, %s)"
#     cursor.execute(sql, (id, question, answer, web_search, law_search))
#     conn.commit()
def insert_id_first_chat(db_connection, question_id, question, first_chat):
    cursor = db_connection.cursor()
    sql = "INSERT INTO baidu_law (question_id, question, first_chat) VALUES (%s, %s, %s)"
    cursor.execute(sql, (question_id, question, first_chat))
    db_connection.commit()
    cursor.close()

def update_web_law_search(db_connection, question_id, web_search, law_search):
    cursor = db_connection.cursor()
    sql = "UPDATE baidu_law SET web_search = %s, law_search = %s WHERE question_id = %s"
    cursor.execute(sql, (web_search, law_search, question_id))
    db_connection.commit()
    cursor.close()

def update_other_chat(db_connection, question_id, other_chat):
    cursor = db_connection.cursor()
    sql = "UPDATE baidu_law SET other_chat = %s WHERE question_id = %s"
    cursor.execute(sql, (other_chat, question_id))
    db_connection.commit()
    cursor.close()

def update_answer(db_connection, question_id, answer):
    cursor = db_connection.cursor()
    sql = "UPDATE baidu_law SET answer = %s WHERE question_id = %s"
    cursor.execute(sql, (answer, question_id))
    db_connection.commit()
    cursor.close()


