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