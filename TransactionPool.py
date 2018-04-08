import random
import copy
from Transaction import Transaction
import math

class TransactionPool:
	''' 
	Nothing in this file has been tested
	'''
	def __init__(self, accountList):
		# List of Transactions (the transaction pool itself)
		self.Transactions = []
		# Deep copy of the account list to determine what the outcomes will be
		# without applying it to the actual account list
		self.modifiedAccountList = copy.deepcopy(accountList)
		# Number of users
		self.numberOfUsers = len(accountList.AccountList)
	
	def GenerateRandomTransactions(self, numberOfTransactions):
		'''
		Generates random transactions
		Input:
			numberOfTransactions: Number of transactions to generate
		'''
		for i in range(0, numberOfTransactions):
			coins = random.randrange(0,50) + random.random()
			fromUser = random.randrange(0, self.numberOfUsers)
			toUser = random.randrange(0, self.numberOfUsers)

			# Ensures the sender is not the receiver
			if toUser == fromUser:
				while toUser == fromUser:
					toUser = random.randrange(0, self.numberOfUsers)

			newTransaction = Transaction(coins, fromUser, toUser)
			self.Transactions.append(newTransaction)

	def GenerateValidTransactions(self, numberOfTransactions):
		'''
		Generates a set of valid transactions, appends to self.Transactions
		Input:
			numberOfTransactions: Number of valid transactions to generate
		'''

		for i in range(0, numberOfTransactions):
			fromUser = random.randrange(0, self.numberOfUsers)

			# Insures that the account balance is not empty
			if self.modifiedAccountList.AccountIsEmpty(fromUser):
				while self.modifiedAccountList.AccountIsEmpty(fromUser):
					fromUser = random.randrange(0, self.numberOfUsers)
			
			# Determines the max amount a user can send
			maxAmountToSend = math.floor(self.modifiedAccountList.AccountBalance(fromUser))

			toUser = random.randrange(0, self.numberOfUsers)

			# Insures that the To address is not the same as the From address
			if toUser == fromUser:
				while toUser == fromUser:
					toUser = random.randrange(0, self.numberOfUsers)

			# Only allow transactions to send up to the senders balance
			# Sometimes the user will have 0.xxx (else)
			if maxAmountToSend != 0:
				coins = random.randrange(0,maxAmountToSend) + random.random()
			else:
				coins = random.random()
				while coins > self.modifiedAccountList.AccountBalance(fromUser):
					coins = random.random()

			# Process the transaction on the modifiedAccountList
			self.modifiedAccountList.ProcessTransaction(fromUser, toUser, coins)

			# Create new transaction
			newTransaction = Transaction(coins, fromUser, toUser)

			# Append transaction to list of transactions
			self.Transactions.append(newTransaction)

	def GeneratePercentInvalidTransactions(self, percent=0.05):
		'''
		To be used as a secondary call to GenerateValidTransactions to generate
		a percentage of those transactions as invalid transactions
		Input: 
			percent: Percentage of valid transactions to be invalid transactions. Initially set to 5%
		'''

		# Generate some number of transactions proportional to a percentage of the 
		# current transactions
		numberOfTransactions = math.floor(len(self.Transactions) * percent)

		for i in range(0, numberOfTransactions):
			fromUser = random.randrange(0, self.numberOfUsers)
			toUser = random.randrange(0, self.numberOfUsers)

			# Insures that the To address is not the same as the From address
			if toUser == fromUser:
				while toUser == fromUser:
					toUser = random.randrange(0, self.numberOfUsers)

			# Insures that the account balance is not empty
			if self.modifiedAccountList.AccountIsEmpty(fromUser):
				while self.modifiedAccountList.AccountIsEmpty(fromUser):
					fromUser = random.randrange(0, self.numberOfUsers)

			accountBalance = self.modifiedAccountList.AccountBalance(fromUser)

			# Coins in transaction will be between the accountBalance + 1 to accountBalance + 1 + up to the account balance in 25% intervals
			coins = random.randrange(math.floor(accountBalance)+1, math.ceil(accountBalance + 1 + (random.randrange(1,4)/4)*accountBalance))

			# Verifies that the transaction is invalid. If not, tries again
			while (accountBalance - coins) >= 0:
				coins = random.randrange(math.floor(accountBalance)+1, math.ceil(accountBalance + 1 + (random.randrange(1,4)/4)*accountBalance))

			newTransaction = Transaction(coins, fromUser, toUser)

			# Adds invalid transaction to transaction list
			self.Transactions.append(newTransaction)



