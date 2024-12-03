import requests

# 要请求挖矿的节点地址
miner_address = "AliceMiner"

# 挖矿请求数据
mine_data = {
    "miner_address": miner_address
}

# 发送挖矿请求
response = requests.post('http://localhost:5000/mine', json=mine_data)

# 打印响应内容
if response.status_code == 200:
    print("Mining successful!")
    print("New Block:", response.json())
else:
    print("Mining failed. Message:", response.json())
