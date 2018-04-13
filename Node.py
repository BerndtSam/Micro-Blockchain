from AccountList import AccountList
from Block import Block

class Node:
	def __init__(self, userID, accountList, masterNodes, transactionPool):
		self.userID = userID
		self.AccountList = accountList
		self.MasterNodes = masterNodes
		self.TransactionPool = transactionPool

		self.InitializeNewBlock()
		self.ProcessTransactions()


	def UpdateTransactionPool(self, transactionPool):
		'''
		Transaction pool gets updated on every block
		Input:
			transactionPool: New transaction pool
		'''
		self.TransactionPool = transactionPool

	def InitializeNewBlock(self):
		''' 
		Initializes new block
		'''
		self.Block = Block(self.userID)

	def AddTransaction(self, transaction):
		'''
		Adds a new transaction to the block after verification
		'''
		if self.AccountList.ProcessTransaction(transaction):
			if not self.Block.AddTransaction(transaction):
				print("NodeID: " + str(self.userID) + " has detected an attempt to double spend")
				print("Invalid Sender: " + str(transaction.senderID) + " Amount of coins: " + str(transaction.coins))
		else:
			print("NodeID: " + str(self.userID) + " has rejected an invalid transaction.")
			print("Invalid sender: " + str(transaction.senderID) + " Amount of coins: " + str(transaction.coins))

	def BlockSolved(self):
		'''
		Asked by main program if this nodes block has been solved
		Output:
			If Block solved: Returns solved block
			If Block not solved: returns None
		'''
		if self.Block.IsSolved():
			return self.Block
		else:
			return None

	def ProcessTransactions(self):
		for transactionIndex in range(0,len(self.TransactionPool)):
			self.AddTransaction(self.TransactionPool[transactionIndex])

