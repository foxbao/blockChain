import hashlib
import time
import threading
import json
import requests
from flask import Flask, request, jsonify

class Transaction:
    def __init__(self, sender, recipient, amount):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount

    def __repr__(self):
        return f"Transaction(sender={self.sender}, recipient={self.recipient}, amount={self.amount})"

class Block:
    def __init__(self, index, previous_hash, timestamp, transactions, hash, nonce):
        self.index = index  # 区块的索引
        self.previous_hash = previous_hash  # 前一个区块的哈希
        self.timestamp = timestamp  # 区块创建时间
        self.transactions = transactions  # 区块内的交易列表
        self.hash = hash  # 当前区块的哈希
        self.nonce = nonce  # 工作量证明的随机数

    def __repr__(self):
        return f"Block(index={self.index}, hash={self.hash}, previous_hash={self.previous_hash}, transactions={self.transactions}, nonce={self.nonce})"
    
    def to_dict(self):
        """自定义方法，返回适合 JSON 序列化的字典格式"""
        return {
            "index": self.index,
            "previous_hash": self.previous_hash,
            "timestamp": self.timestamp,
            "transactions": [tx if isinstance(tx, dict) else tx.__dict__ for tx in self.transactions],  # 检查是否是字典类型
            "hash": self.hash,
            "nonce": self.nonce
        }

class Blockchain:
    def __init__(self, difficulty=4):
        self.chain = []  # 存储区块链
        self.pending_transactions = []  # 存储待处理的交易
        self.difficulty = difficulty  # 工作量证明的难度
        self.create_genesis_block()  # 创建创世区块（第一个区块）
        self.nodes = set()  # 存储网络中其他节点的地址

    def create_genesis_block(self):
        # 创世区块（第一个区块）
        genesis_block = Block(0, "0", int(time.time()), [], self.calculate_hash(0, "0", int(time.time()), [], 0), 0)
        self.chain.append(genesis_block)

    def calculate_hash(self, index, previous_hash, timestamp, transactions, nonce):
        # 计算区块的哈希值
        block_string = f"{index}{previous_hash}{timestamp}{[str(tx) for tx in transactions]}{nonce}".encode('utf-8')
        return hashlib.sha256(block_string).hexdigest()

    def add_transaction(self, sender, recipient, amount):
        # 添加交易到待处理交易池
        transaction = Transaction(sender, recipient, amount)
        self.pending_transactions.append(transaction)
        print(f"Transaction added: {transaction}")

    def mine_block(self, miner_address)->Block:
        # 挖矿：获取当前待处理交易的列表并创建新区块
        if not self.pending_transactions:
            return False

        # 挖矿的过程：通过工作量证明找到合适的 nonce
        last_block = self.chain[-1]
        new_index = last_block.index + 1
        timestamp = int(time.time())
        transactions_to_mine = self.pending_transactions
        nonce = 0

        # 不断计算哈希直到找到符合条件的哈希值（前面有指定数量的零）
        new_hash = self.calculate_hash(new_index, last_block.hash, timestamp, transactions_to_mine, nonce)
        while not new_hash.startswith('0' * self.difficulty):
            nonce += 1
            new_hash = self.calculate_hash(new_index, last_block.hash, timestamp, transactions_to_mine, nonce)

        # 创建新区块并加入链中
        new_block = Block(new_index, last_block.hash, timestamp, transactions_to_mine, new_hash, nonce)
        self.chain.append(new_block)

        # 清空交易池
        self.pending_transactions = []

        # 奖励矿工
        self.add_transaction("System", miner_address, 50)  # 假设矿工奖励为50个单位

        # 打印挖矿完成的信息
        print(f"Mining completed. Block mined: {new_block}")
        return new_block

    def is_valid(self):
        # 验证区块链的有效性
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            # 校验当前区块的哈希是否匹配
            if current_block.hash != self.calculate_hash(current_block.index, current_block.previous_hash, current_block.timestamp, current_block.transactions, current_block.nonce):
                return False

            # 校验当前区块的前哈希是否匹配
            if current_block.previous_hash != previous_block.hash:
                return False

        return True

    def add_node(self, node_address):
        # 向区块链网络中添加新节点
        self.nodes.add(node_address)

    def broadcast_new_block(self, block:Block):
        # 将新区块广播到网络中的其他节点
        for node in self.nodes:
            try:
                requests.post(f"http://{node}/add_block", json=block.to_dict())
            except requests.exceptions.RequestException as e:
                print(f"Error broadcasting to {node}: {e}")

    def sync_chain(self):
        # 从其他节点拉取区块链数据
        for node in self.nodes:
            try:
                response = requests.get(f"http://{node}/get_chain")
                if response.status_code == 200:
                    new_chain = response.json()["chain"]
                    if len(new_chain) > len(self.chain):
                        self.chain = new_chain
            except requests.exceptions.RequestException as e:
                print(f"Error syncing with {node}: {e}")


# Flask Web 服务来模拟区块链节点
app = Flask(__name__)
blockchain = Blockchain()

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    data = request.get_json()
    blockchain.add_transaction(data['sender'], data['recipient'], data['amount'])
    return jsonify({"message": "Transaction added lalala"}), 201

@app.route('/mine', methods=['POST'])
def mine():
    data = request.get_json()
    miner_address = data['miner_address']
    new_block = blockchain.mine_block(miner_address)
    if new_block:
        blockchain.broadcast_new_block(new_block)
        return jsonify({"message": "Block mined", "block": new_block.to_dict()}), 200
        # return jsonify({"message": "Block mined", "block": "lalala"}), 200
    return jsonify({"message": "No transactions to mine"}), 400

@app.route('/add_block', methods=['POST'])
def add_block():
    data = request.get_json()
    block = Block(**data)
    blockchain.chain.append(block)
    print(f"Block added: {block}")
    return jsonify({"message": "Block added"}), 201

@app.route('/get_chain', methods=['GET'])
def get_chain():
    return jsonify({"chain": [block.__dict__ for block in blockchain.chain]}), 200

@app.route('/add_node', methods=['POST'])
def add_node():
    data = request.get_json()
    blockchain.add_node(data['node_address'])
    return jsonify({"message": f"Node {data['node_address']} added"}), 200

@app.route('/get_blocks', methods=['GET'])
def get_blocks():
    # 返回所有区块
    return jsonify({"blocks": [block.to_dict() for block in blockchain.chain]}), 200

# 启动 Flask Web 服务
def run_node(port):
    app.run(host='0.0.0.0', port=port)

# 启动三个节点
if __name__ == "__main__":
    # 启动节点1
    node_thread_1 = threading.Thread(target=run_node, args=(5000,))
    node_thread_1.start()

    # 启动节点2
    node_thread_2 = threading.Thread(target=run_node, args=(5001,))
    node_thread_2.start()

    # 启动节点3
    node_thread_3 = threading.Thread(target=run_node, args=(5002,))
    node_thread_3.start()

    # 添加一些初始交易
    blockchain.add_transaction("Alice", "Bob", 10)
    blockchain.add_transaction("Bob", "Charlie", 20)
    blockchain.add_transaction("Charlie", "Alice", 30)

    # 模拟三个用户参与挖矿
    blockchain.add_node("localhost:5000")
    blockchain.add_node("localhost:5001")
    blockchain.add_node("localhost:5002")
