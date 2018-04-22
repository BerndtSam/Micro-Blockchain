class Transaction:
	def __init__(self, coins, senderID, receiverID):
		self.coins = coins
		self.senderID = senderID
		self.receiverID = receiverID
		self.processed = False