from AccountList import AccountList
from Block import Block
from threading import Timer
import threading
import random
import copy
import math

class Node:
	def __init__(self, userID, accountList, blocksSolved, transactionPool, microBlocksPerBlock, maxTimePerMicroBlock):
		self.userID = userID
		self.BlocksSolved = blocksSolved
		self.OriginalAccountList = copy.deepcopy(accountList)
		self.ModifiedAccountList = copy.deepcopy(accountList)
		self.MasterNodes = []
		self.TransactionPool = transactionPool
		self.MasterNode = False
		self.NextBlockReady = False
		self.Nodes = []
		self.MicroBlocksPerBlock = microBlocksPerBlock
		self.MaxTimePerMicroBlock = maxTimePerMicroBlock
		self.Block = None

		self.InitializeNewBlock()
		#self.ProcessTransactions()
		self.TransactionThread = threading.Thread(target=self.ProcessTransactions)
		self.TransactionThread.start()
		#self.ProcessTransactions()


	def UpdateTransactionPool(self, transactionPool):
		'''
		Transaction pool gets updated on every block
		Input:
			transactionPool: New transaction pool
		'''
		if self.MasterNode == True:
			return
		self.TransactionPool = transactionPool

	def InitializeNewBlock(self):
		''' 
		Initializes new block
		'''
		if self.MasterNode == True:
			return
		self.Block = Block(self.userID, self.MicroBlocksPerBlock, self.MaxTimePerMicroBlock)

	def AddTransaction(self, transaction):
		'''
		Adds a new transaction to the block after verification
		'''
		if self.ModifiedAccountList.ProcessTransaction(transaction):
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
		'''
		Processes all transactions for current block from self.TransactionPool
		'''
		if self.MasterNode == True:
			return

		# Need to break up set of transactions so that all microblocks can hold transactions
		TransactionSplitIndex = float(len(self.TransactionPool))/float(self.MicroBlocksPerBlock)
		for microBlock in range(0, self.MicroBlocksPerBlock):
			for transactionIndex in range(math.floor(TransactionSplitIndex*microBlock),math.floor(TransactionSplitIndex*(microBlock+1))):
				self.AddTransaction(self.TransactionPool[transactionIndex])
			
			# Ensures all transactions are processed in case of floor rounding error
			if microBlock == self.MicroBlocksPerBlock-1:
				for transactionIndex in range(math.floor(TransactionSplitIndex*(microBlock+1)), len(self.TransactionPool)):
					self.AddTransaction(self.TransactionPool[transactionIndex])

			# Makes it so each microblock will contain transactions (waits for new microblock to be ready before continuing)
			while self.Block.CheckMicroBlockStatus() != True:
				continue


	def SetMasterNode(self, masterNode):
		'''
		Sets whether this is a masternode or not. If so, sets up appropriate parameters
		Input:
			masterNode: Sets if this node is enabled as a masternode
		'''
		if masterNode == True:
			self.MasterNode = True
		else:
			self.MasterNode = False

	def IsMasterNode(self):
		'''
		Returns if the current node is set to be a masternode
		Output:
			self.Masternode
		'''
		return self.MasterNode

	def SetMasterNodes(self, masterNodes):
		'''
		Sets list of masternodes to given masterNodes
		Input:
			masterNodes: List of masterNodes
		'''
		self.MasterNodes = masterNodes

	def SetNodes(self, nodes):
		'''
		Sets list of nodes to given nodes
		Input:
			nodes: List of nodes
		'''
		self.Nodes = nodes

	def WaitForTransactionProcessing(self):
		'''
		Allows transactions to be processed at separate times without halting machine
		'''
		self.NextBlockReady = True
		return



