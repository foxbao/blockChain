import requests

# 发送交易请求
transaction_data = {
    "sender": "Alice",
    "recipient": "Bob",
    "amount": 10
}

response = requests.post('http://localhost:5008/add_transaction', json=transaction_data)

# 打印响应内容
print(response.status_code)
print(response.json())
