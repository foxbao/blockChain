import socket
import threading
import json
import time
import hashlib

# 区块类
class Block:
    def __init__(self, index, previous_hash, timestamp, data, hash_value, nonce=0):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
        self.hash_value = hash_value
        self.nonce = nonce

    def __repr__(self):
        return f"Block(index={self.index}, hash={self.hash_value[:10]}, nonce={self.nonce})"

# 工作量证明（PoW）类
class PoW:
    def __init__(self, difficulty=4):
        self.difficulty = difficulty

    def mine(self, block):
        block.nonce = 0
        while True:
            block_data = f"{block.index}{block.previous_hash}{block.timestamp}{block.data}{block.nonce}"
            hash_value = hashlib.sha256(block_data.encode()).hexdigest()
            if hash_value[:self.difficulty] == '0' * self.difficulty:
                return hash_value
            block.nonce += 1

# 区块链类
class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.difficulty = 4
        self.pow = PoW(self.difficulty)
        self.pending_transactions = []

    def create_genesis_block(self):
        return Block(0, "0", int(time.time()), "Genesis Block", "0" * 64)

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, block):
        self.chain.append(block)

    def mine_block(self, data):
        latest_block = self.get_latest_block()
        timestamp = int(time.time())
        new_block = Block(latest_block.index + 1, latest_block.hash_value, timestamp, data, "")
        new_block_hash = self.pow.mine(new_block)
        new_block.hash_value = new_block_hash
        self.add_block(new_block)
        return new_block

    def get_chain(self):
        return self.chain

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            block_data = f"{current_block.index}{current_block.previous_hash}{current_block.timestamp}{current_block.data}{current_block.nonce}"
            if current_block.hash_value != hashlib.sha256(block_data.encode()).hexdigest():
                return False
            if current_block.previous_hash != previous_block.hash_value:
                return False
        return True

    def add_transaction(self, transaction):
        self.pending_transactions.append(transaction)

    def process_transactions(self):
        if self.pending_transactions:
            transaction_data = json.dumps(self.pending_transactions, sort_keys=True)
            new_block = self.mine_block(transaction_data)
            self.pending_transactions = []
            return new_block
        return None

# 网络节点类
class Node:
    def __init__(self, host, port, blockchain):
        self.host = host
        self.port = port
        self.blockchain = blockchain
        self.peers = []  # 其他节点的地址
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen(5)

    def start(self):
        print(f"Node started at {self.host}:{self.port}")
        threading.Thread(target=self.listen_for_connections).start()

    def listen_for_connections(self):
        while True:
            client_socket, client_address = self.server.accept()
            print(f"Connection established with {client_address}")
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):
        data = client_socket.recv(1024).decode('utf-8')
        if data:
            print(f"Received data: {data}")
            self.process_received_data(data)
        client_socket.close()

    def process_received_data(self, data):
        try:
            message = json.loads(data)
            if message['type'] == 'block':
                block = Block(**message['block'])
                self.blockchain.add_block(block)
                print(f"Block added to blockchain: {block}")
            elif message['type'] == 'transaction':
                self.blockchain.add_transaction(message['transaction'])
                print(f"Transaction added: {message['transaction']}")
            elif message['type'] == 'peer':
                self.peers.append(message['peer'])
                print(f"New peer added: {message['peer']}")
        except Exception as e:
            print(f"Error processing data: {e}")

    def broadcast_block(self, block):
        message = {
            'type': 'block',
            'block': block.__dict__
        }
        self.send_to_peers(message)

    def broadcast_transaction(self, transaction):
        message = {
            'type': 'transaction',
            'transaction': transaction
        }
        self.send_to_peers(message)

    def send_to_peers(self, message):
        for peer in self.peers:
            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_socket.connect((peer[0], peer[1]))
            peer_socket.send(json.dumps(message).encode('utf-8'))
            peer_socket.close()

    def add_peer(self, peer_host, peer_port):
        self.peers.append((peer_host, peer_port))
        message = {
            'type': 'peer',
            'peer': (self.host, self.port)
        }
        self.send_to_peers(message)

# 模拟区块链网络
def simulate_blockchain_network():
    blockchain1 = Blockchain()
    blockchain2 = Blockchain()

    node1 = Node('localhost', 5010, blockchain1)
    node2 = Node('localhost', 5011, blockchain2)

    node1.start()
    node2.start()

    time.sleep(1)  # 等待节点启动完成

    # 添加节点 peer
    node1.add_peer('localhost', 5011)
    node2.add_peer('localhost', 5010)

    # 模拟一个交易
    node1.blockchain.add_transaction({"from": "Alice", "to": "Bob", "amount": 10})
    node1.blockchain.process_transactions()

    # 模拟区块广播
    new_block = node1.blockchain.mine_block("Block data")
    node1.broadcast_block(new_block)
    aaaaa=1

if __name__ == "__main__":
    simulate_blockchain_network()
