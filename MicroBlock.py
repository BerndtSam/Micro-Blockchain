from threading import Timer
import random

class MicroBlock:
	def __init__(self, blockID, microBlockID, maxTimePerMicroBlock):
		self.BlockID = blockID
		self.MicroBlockID = microBlockID
		
		# How long each microblock takes
		Timer(random.randint(1,maxTimePerMicroBlock), self.MicroBlockSolved).start()
		self.TransactionList = []
		self.Solved = False


	def AddTransaction(self, transaction):
		'''
		Adds the transaction to this micro blocks list of transactions if it doesn't already exist
		Input:
			transaction: Transaction object to add to list for future processing
		Output:
			True: If the transaction was sucessfully added and wasn't already present in the list
			False: If the transaction was not successfully added as it already existed in the list
		'''
		if transaction not in self.TransactionList:
			self.TransactionList.append(transaction)
			return True
		else:
			return False

	def RemoveTransaction(self, transaction):
		'''
		Removes the given transaction from this micro blocks list of transactions if it exists
		Input:
			transaction: Transaction object to remove from list of transactions, if it exists
		Output:
			True: If the transaction object exists in the list and was sucessfully removed
			False: If the transaction object does not exist in the list and thus was not removed
		'''
		if transaction in self.TransactionList:
			self.TransactionList.remove(transaction)
			return True
		else:
			return False

	def MicroBlockSolved(self):
		'''
		Sets the microblock to solved
		'''
		self.Solved = True
		#print("MicroBlock " + str(self.MicroBlockID) + " solved by: " + str(self.BlockID))

	def IsSolved(self):
		'''
		Returns whether the microblock is solved
		Output:
			True: If the microblock is solved
			False: If the microblock is not solved
		'''
		return self.Solved


