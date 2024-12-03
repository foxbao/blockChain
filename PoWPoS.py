import hashlib
import random
import time

# 模拟一个区块
class Block:
    def __init__(self, index, previous_hash, timestamp, data, hash_value):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
        self.hash_value = hash_value

    def __repr__(self):
        return f"Block(index={self.index}, hash={self.hash_value[:10]})"

# 工作量证明（PoW）模拟
class PoWNode:
    def __init__(self, node_id):
        self.node_id = node_id
        self.difficulty = 4  # 定义挖矿难度（前面需要有多少个零）
    
    def mine_block(self, index, previous_hash, data):
        timestamp = int(time.time())
        nonce = 0
        while True:
            block_data = f"{index}{previous_hash}{timestamp}{data}{nonce}"
            hash_value = hashlib.sha256(block_data.encode()).hexdigest()
            if hash_value[:self.difficulty] == '0' * self.difficulty:  # 挖到符合难度要求的哈希
                return Block(index, previous_hash, timestamp, data, hash_value)
            nonce += 1

# 权益证明（PoS）模拟
class PoSNode:
    def __init__(self, node_id, stake):
        self.node_id = node_id
        self.stake = stake  # 每个节点的权益（持有的代币数）

    def select_block_producer(self, nodes):
        # 通过节点权益随机选择一个节点作为区块生产者
        total_stake = sum(node.stake for node in nodes)
        random_choice = random.uniform(0, total_stake)
        current_stake = 0
        for node in nodes:
            current_stake += node.stake
            if current_stake >= random_choice:
                return node
        return nodes[0]  # 默认返回第一个节点

# 模拟区块链
class Blockchain:
    def __init__(self, consensus_type='PoW'):
        self.chain = [self.create_genesis_block()]
        self.consensus_type = consensus_type
        self.nodes = []
    
    def create_genesis_block(self):
        return Block(0, "0", int(time.time()), "Genesis Block", "0000000000000000")

    def add_block(self, new_block):
        self.chain.append(new_block)

    def mine_block(self, data):
        if self.consensus_type == 'PoW':
            miner = PoWNode("miner1")
            last_block = self.chain[-1]
            new_block = miner.mine_block(last_block.index + 1, last_block.hash_value, data)
            self.add_block(new_block)
            print(f"PoW: Block mined by {miner.node_id} - {new_block}")
        elif self.consensus_type == 'PoS':
            producer = self.nodes[0].select_block_producer(self.nodes)  # 随机选择一个节点作为区块生产者
            last_block = self.chain[-1]
            new_block = Block(last_block.index + 1, last_block.hash_value, int(time.time()), data, "pos_block_hash")
            self.add_block(new_block)
            print(f"PoS: Block produced by {producer.node_id} with stake {producer.stake} - {new_block}")

    def add_nodes(self, nodes):
        self.nodes.extend(nodes)

# 模拟运行
if __name__ == "__main__":
    # 模拟一个PoW区块链
    print("----- PoW Blockchain -----")
    pow_blockchain = Blockchain(consensus_type='PoW')
    pow_blockchain.mine_block("Block 1 data")
    pow_blockchain.mine_block("Block 2 data")
    
    # 模拟一个PoS区块链
    print("\n----- PoS Blockchain -----")
    pos_blockchain = Blockchain(consensus_type='PoS')
    # 创建一些节点，每个节点有不同的权益
    pos_nodes = [PoSNode("Node1", 50), PoSNode("Node2", 30), PoSNode("Node3", 20)]
    pos_blockchain.add_nodes(pos_nodes)
    pos_blockchain.mine_block("Block 1 data")
    pos_blockchain.mine_block("Block 2 data")
