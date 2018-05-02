import random
import copy
from Transaction import Transaction
import math

class TransactionPool:
	def __init__(self, accountList):
		# List of Transactions (the transaction pool itself)
		self.Transactions = []
		# Deep copy of the account list to determine what the outcomes will be
		# without applying it to the actual account list
		self.modifiedAccountList = copy.deepcopy(accountList)
		# Deep copy of the account list to maintain the original balance for 
		# valid transactions
		self.originalAccountList = copy.deepcopy(accountList)
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

	def ValidFromUser(self, availableFromUsers, previousTransactionList):
		'''
		Generates a valid from user for a transaction.
		Valid is defined as not having already been in a transaction this block
		and not having an empty account
		Input:
			availableFromUsers: Accounts who have not been in a transaction this block
			previousTransactionList: List of unprocessed transactions to account for in this grouping
		Output:
			validUser: Valid user ID for from transaction
		'''
		validUser = False
		previousTransactions = [transaction.senderID for transaction in previousTransactionList]

		while validUser != True:
			# Randomly select a user from list of availableUsers
			fromUser = availableFromUsers[random.randrange(0, len(availableFromUsers))]

			if not self.originalAccountList.AccountIsEmpty(fromUser) and fromUser not in previousTransactions:
				validUser = True

		return fromUser


	def GenerateValidTransactions(self, numberOfTransactions, previousTransactionList):
		'''
		Generates a set of valid ordered transactions, appends to self.Transactions.
		Does not allow more than one transaction per block
		Input:
			numberOfTransactions: Number of valid transactions to generate
			previousTransactionList: List of unprocessed transactions to account for in this grouping
		'''
		print('Generating valid Transactions')
		availableFromUsers = [user for user in range(0,self.numberOfUsers)]

		for i in range(0, numberOfTransactions):
			# Generate a valid from user who has not been in a transaction this block
			# and whose account is not empty
			fromUser = self.ValidFromUser(availableFromUsers, previousTransactionList)
			availableFromUsers.remove(fromUser)
			
			# Determines the max amount a user can send
			maxAmountToSend = math.floor(self.originalAccountList.AccountBalance(fromUser))

			# Only allow transactions to send up to the senders balance
			# Sometimes the user will have 0.xxx (else)
			if maxAmountToSend != 0:
				try:
					coins = random.randrange(0,maxAmountToSend) + random.random()
				except:
					print('Invalid "Valid" transaction sending ' + str(maxAmountToSend) + ' coins from ' +  str(fromUser))
					print(self.originalAccountList.AccountList)
					continue
			else:
				coins = random.random()
				while coins > self.originalAccountList.AccountBalance(fromUser):
					coins = random.random()

			toUser = random.randrange(0, self.numberOfUsers)

			# Insures that the To address is not the same as the From address
			if toUser == fromUser:
				while toUser == fromUser:
					toUser = random.randrange(0, self.numberOfUsers)

			# Create new transaction
			newTransaction = Transaction(coins, fromUser, toUser)

			# Process the transaction on the modifiedAccountList
			self.modifiedAccountList.ProcessTransaction(newTransaction)

			# Append transaction to list of transactions
			self.Transactions.append(copy.deepcopy(newTransaction))

	def GeneratePercentInvalidTransactions(self, percent=0.05):
		'''
		To be used as a secondary call to GenerateValidTransactions to generate
		a percentage of those transactions as invalid transactions
		Input: 
			percent: Percentage of valid transactions to be invalid transactions. Initially set to 5%
		'''
		# TODO: Integrate this into the main program

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

	def ReinitializeTransactionPool(self, accountList, rolloverTransactions):
		'''
		Used to reinitialize the transaction pool for the next iteration
		Input:
			accountList: Account list to generate transactions from
			rolloverTransactions: Transactions that were not processed in the last iteration
		'''
		# List of Transactions (the transaction pool itself)
		self.Transactions = rolloverTransactions
		# Deep copy of the account list to determine what the outcomes will be
		# without applying it to the actual account list
		self.modifiedAccountList = copy.deepcopy(accountList)
		# Deep copy of the account list to maintain the original balance for 
		# valid transactions
		self.originalAccountList = copy.deepcopy(accountList)

