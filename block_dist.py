import hashlib
import json
import time
import random
import requests
from flask import Flask, jsonify, request

# 区块类
class Block:
    def __init__(self, index, previous_hash, timestamp, transactions, proof, hash):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.transactions = transactions
        self.proof = proof
        self.hash = hash

# 区块链类
class Blockchain:
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.nodes = set()  # 用于存储其他节点
        self.create_genesis_block()

    # 创建创世区块
    def create_genesis_block(self):
        self.create_block(proof=100, previous_hash='1')

    # 创建新的区块
    def create_block(self, proof, previous_hash=None):
        block = Block(
            index=len(self.chain) + 1,
            previous_hash=previous_hash or self.hash(self.chain[-1]),
            timestamp=time.time(),
            transactions=self.transactions,
            proof=proof,
            hash=self.hash(self.transactions)
        )
        self.transactions = []  # 清空当前的交易列表
        self.chain.append(block)
        return block

    # 计算区块的哈希
    @staticmethod
    def hash(block):
        # 如果是一个区块对象，则应该序列化整个区块的属性
        if isinstance(block, Block):
            block_string = json.dumps(block.__dict__, sort_keys=True).encode()
        else:
            # 如果是交易列表，则直接将其转化为字符串进行哈希
            block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    # 验证一个区块的有效性
    def validate_block(self, block, previous_block):
        if previous_block.index + 1 != block.index:
            return False
        if previous_block.hash != block.previous_hash:
            return False
        if self.hash(block.transactions) != block.hash:
            return False
        return True

    # 挖掘新区块（Proof of Work）
    def proof_of_work(self, previous_proof):
        proof = 0
        while self.valid_proof(previous_proof, proof) is False:
            proof += 1
        return proof

    # 验证工作证明
    @staticmethod
    def valid_proof(previous_proof, proof):
        guess = f'{previous_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == '0000'

    # 添加交易
    def add_transaction(self, sender, recipient, amount):
        self.transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        })
        return self.chain[-1].index + 1

    # 获取最新区块
    def last_block(self):
        return self.chain[-1]

    # 同步区块链
    def register_node(self, address):
        self.nodes.add(address)

    # 同步区块链
    def resolve_conflicts(self):
        neighbour_chains = []
        max_length = len(self.chain)

        for node in self.nodes:
            response = requests.get(f'http://{node}/chain')
            if response.status_code == 200:
                chain = response.json()['chain']
                length = len(chain)
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    neighbour_chains = chain

        if neighbour_chains:
            self.chain = neighbour_chains
            return True

        return False

    # 验证整个区块链是否有效
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        for block in chain[1:]:
            if not self.validate_block(block, previous_block):
                return False
            previous_block = block
        return True

# 用户节点类
class Node:
    def __init__(self, address, blockchain):
        self.address = address
        self.blockchain = blockchain
        self.blockchain.register_node(address)

    # 挖矿并创建新区块
    def mine(self):
        last_block = self.blockchain.last_block()
        proof = self.blockchain.proof_of_work(last_block.proof)
        self.blockchain.add_transaction(sender='0', recipient=self.address, amount=1)
        block = self.blockchain.create_block(proof, last_block.hash)
        return block

    # 注册交易
    def create_transaction(self, sender, recipient, amount):
        return self.blockchain.add_transaction(sender, recipient, amount)

# 创建Flask应用
app = Flask(__name__)

# 创建区块链和节点
blockchain = Blockchain()
node_1 = Node(address="localhost:5001", blockchain=blockchain)
node_2 = Node(address="localhost:5002", blockchain=blockchain)
node_3 = Node(address="localhost:5003", blockchain=blockchain)

# 模拟三笔交易
node_1.create_transaction(sender="User1", recipient="User2", amount=10)
node_1.create_transaction(sender="User2", recipient="User3", amount=5)
node_2.create_transaction(sender="User3", recipient="User1", amount=7)

# 挖矿并创建区块
node_1.mine()
node_2.mine()
node_3.mine()

# 获取区块链信息
@app.route('/chain', methods=['GET'])
def get_chain():
    chain = []
    for block in blockchain.chain:
        chain.append(block.__dict__)
    return jsonify({'chain': chain, 'length': len(chain)})

# 添加交易
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    values = request.get_json()
    if not values or 'sender' not in values or 'recipient' not in values or 'amount' not in values:
        return 'Missing values', 400
    sender = values['sender']
    recipient = values['recipient']
    amount = values['amount']
    block_index = blockchain.add_transaction(sender, recipient, amount)
    return jsonify({'message': f'Transaction will be added to Block {block_index}'}), 201

# 同步区块链
@app.route('/resolve', methods=['GET'])
def resolve():
    replaced = blockchain.resolve_conflicts()
    if replaced:
        return jsonify({'message': 'Chain was replaced', 'new_chain': [block.__dict__ for block in blockchain.chain]})
    return jsonify({'message': 'Chain is up-to-date'})


if __name__ == '__main__':
    app.run(port=5008)
