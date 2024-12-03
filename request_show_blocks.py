import requests

# 发送请求以获取所有区块
def get_all_blocks():
    response = requests.get("http://localhost:5000/get_blocks")
    
    if response.status_code == 200:
        blocks = response.json().get("blocks", [])
        if blocks:
            print(f"Total blocks in the chain: {len(blocks)}")
            for block in blocks:
                print(f"Block {block['index']} - Hash: {block['hash']}")
                print(f"  Previous Hash: {block['previous_hash']}")
                print(f"  Transactions: {block['transactions']}")
        else:
            print("No blocks found.")
    else:
        print(f"Failed to get blocks. Status code: {response.status_code}")

# 调用函数，打印所有区块
get_all_blocks()
