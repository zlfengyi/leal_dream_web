import sqlite3

# 连接到数据库，如果数据库不存在，则会创建一个新的数据库
conn = sqlite3.connect('instance/tweets.db')

# 创建一个cursor对象
cur = conn.cursor()

# 执行查询
cur.execute("SELECT * FROM tweet")

# 获取查询结果
rows = cur.fetchall()

# 遍历结果并打印
for row in rows:
    print(row)

# 关闭连接
conn.close()
