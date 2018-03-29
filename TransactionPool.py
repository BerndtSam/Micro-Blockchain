import random
import copy

class TransactionPool:
	''' 
	Nothing in this file has been tested
	'''
	def __init__(self):
		self.Transactions = []
		self.EmptyTransaction = {'From': None, 'To': None, 'Coins': None}
	
	def GenerateRandomTransactions(self, numberOfTransactions, numberOfUsers):
		for i in range(0, numberOfTransactions):
			tempTransaction = copy.deepcopy(self.EmptyTransaction)
			tempTransaction['From'] = random.randrange(0,numberOfUsers)
			tempTransaction['To'] = random.randrange(0,numberOfUsers)
			if tempTransaction['To'] == tempTransaction['From']:
				while tempTransaction['To'] == tempTransaction['From']:
					tempTransaction['To'] = random.randrange(0,numberOfUsers)
			tempTransaction['Coins'] = random.randrange(0,50) + random.random()

			self.Transactions.append(tempTransaction)

	def GenerateValidTransactions(self, accountList, numberOfTransactions, numberOfUsers):
		for i in range(0, numberOfTransactions):
			tempTransaction = copy.deepcopy(self.EmptyTransaction)
			
			tempTransaction['From'] = random.randrange(0,numberOfUsers)

			# Insures that the account balance is not empty
			if accountList.AccountIsEmpty(tempTransaction['From']):
				while accountList.AccountIsEmpty(tempTransaction['From']):
					tempTransaction['From'] = random.randrange(0,numberOfUsers)
			
			# Determines the max amount a user can send
			maxAmountToSend = accountList.AccountBalance(tempTransaction['From'])

			tempTransaction['To'] = random.randrange(0,numberOfUsers)

			# Insures that the To address is not the same as the From address
			if tempTransaction['To'] == tempTransaction['From']:
				while tempTransaction['To'] == tempTransaction['From']:
					tempTransaction['To'] = random.randrange(0,numberOfUsers)

			# Only allow transactions to send up to the senders balance
			tempTransaction['Coins'] = random.randrange(0,maxAmountToSend-1) + random.random()

			self.Transactions.append(tempTransaction)