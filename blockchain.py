import hashlib
import time
from transaction import Transaction

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

    
class Blockchain:
    def __init__(self,difficulty=4):
        self.chain=[]
        self.pending_transactions=[]
        self.difficulty=difficulty
        self.create_genesis_block()  # 创建创世区块（第一个区块）
        
    def create_genesis_block(self):
        # 创世区块（第一个区块）
        genesis_block = Block(0, "0", int(time.time()), [], self.calculate_hash(0, "0", int(time.time()), [], 0), 0)
        self.chain.append(genesis_block)
        
    def calculate_hash(self, index, previous_hash, timestamp, transactions, nonce):
        # 计算区块的哈希值
        block_string = f"{index}{previous_hash}{timestamp}{[str(tx) for tx in transactions]}{nonce}".encode('utf-8')
        return hashlib.sha256(block_string).hexdigest()
    
    def add_transaction(self,sender,recipient,amount):
        transaction=Transaction(sender,recipient,amount)
        self.pending_transactions.append(transaction)
        
    def mine_block(self,miner_address):
        if not self.pending_transactions:
            return False
        last_block=self.chain[-1]
        new_index=last_block.index+1
        timestamp = int(time.time())
        transactions_to_mine=self.pending_transactions
        nonce=0
        
        new_hash = self.calculate_hash(new_index, last_block.hash, timestamp, transactions_to_mine, nonce)
        
        while not new_hash.startswith('0' * self.difficulty):
            nonce+=1
            new_hash = self.calculate_hash(new_index, last_block.hash, timestamp, transactions_to_mine, nonce)

        # 创建新区块并加入链中
        new_block = Block(new_index, last_block.hash, timestamp, transactions_to_mine, new_hash, nonce)
        self.chain.append(new_block)

        # 清空交易池
        self.pending_transactions = []
        # 奖励矿工
        self.add_transaction("System", miner_address, 50)  # 假设矿工奖励为50个单位

        return new_block
        
        
    def add_block(self,data):
        previous_block =self.chain[-1]
        new_index=previous_block.index+1
        new_timestamp=int(time.time())
        new_hash=self.calculate_hash(new_index,previous_block.hash,new_timestamp,data)
        new_block=Block(new_index,previous_block.hash,new_timestamp,data,new_hash)
        self.chain.append(new_block)

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

if __name__ == "__main__":
    # 测试区块链功能
    blockchain = Blockchain(difficulty=4)  # 设置挖矿难度为4
    # 添加交易
    blockchain.add_transaction("Alice", "Bob", 10)
    blockchain.add_transaction("Bob", "Charlie", 20)
    # 挖矿：矿工进行工作量证明并生成新区块
    new_block = blockchain.mine_block("Miner1")
    print(f"Block mined: {new_block}")
    # 添加更多交易并继续挖矿
    blockchain.add_transaction("Charlie", "Alice", 30)
    blockchain.add_transaction("Alice", "Bob", 40)

    new_block = blockchain.mine_block("Miner2")
    print(f"Block mined: {new_block}")
    
    # 打印区块链中的所有区块
    for block in blockchain.chain:
        print(block)

    # 验证区块链是否有效
    print("\nIs the blockchain valid?", blockchain.is_valid())