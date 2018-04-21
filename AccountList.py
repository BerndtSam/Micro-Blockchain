import copy
import random
import statistics
from Transaction import Transaction

class AccountList:
	def __init__(self, accountList={}):
		self.AccountList = accountList
		self.EmptyAccountListEntry = {'NumberOfBlocksSolved':0, 'Balance':0}

	def PopulateAccountList(self, numberOfUsers, rand=False):
		'''
		Populates the account list with either empty or random values
		Input:
			numberOfUsers: The number of users to populate the account list with
			rand: Boolean determining if the account list should be populated with random values
		'''
		for i in range(0,numberOfUsers):
			if rand == True:
				self.AccountList[i] = copy.deepcopy(self.EmptyAccountListEntry)
				if random.random() > 0.5:
					self.AccountList[i]['NumberOfBlocksSolved'] = random.randrange(0, 101)
				else:
					self.AccountList[i]['NumberOfBlocksSolved'] = 0

				self.AccountList[i]['Balance'] = random.randrange(0, 101) + random.random()
			
			else:
				self.AccountList[i] = copy.deepcopy(self.EmptyAccountListEntry)

	def AddToBalance(self, address, coins):
		'''
		Adds coins to balance of address
		Input:
			address: Address of user to add coins to balance
			coins: Coins to add to address balance
		'''
		self.AccountList[address]['Balance'] += coins

	def RemoveFromBalance(self, address, coins):
		'''
		Removes coins from balance of address if the balance after the transaction is greater or equal to 0
		Input:
			address: Address of user to remove coins from balance
			coins: Coins to remove from address balance
		Output:
			True: If removing those coins from balance doesn't cause balance to go below 0
			False: If removing coins causes balance to go below 0
		'''
		if (self.AccountList[address]['Balance'] - coins) >= 0:
			self.AccountList[address]['Balance'] -= coins
			return True
		else:
			return False

	def AddBlock(self, address):
		'''
		Adds block to NumberOfBlocks solved to address
		Input:
			address: Address of user to add a solved block to
		'''
		self.AccountList[address]['NumberOfBlocksSolved'] += 1

	def MedianBlocksSolved(self):
		'''
		Determines the median number of blocks solved out of the account list
		Output:
			return the median number of blocks solved
		'''
		BlocksSolved = []
		for accountNumber in self.AccountList:
			if self.AccountList[accountNumber]['NumberOfBlocksSolved'] != 0:
				BlocksSolved.append(self.AccountList[accountNumber]['NumberOfBlocksSolved'])
		return statistics.median(BlocksSolved)

	def ProcessTransaction(self, transaction):
		'''
		Processes a transaction from a sender to a receiver
		Input:
			transaction: Transaction object which contains senderID, receiverID, and coins sent
		Output:
			True: If the transaction is carried out successfully
			False: If there was insufficient funds in the transaction
		'''
		if self.RemoveFromBalance(transaction.senderID, transaction.coins):
			self.AddToBalance(transaction.receiverID, transaction.coins)
			return True
		else:
			return False

	def AccountIsEmpty(self, address):
		'''
		Returns if the account is empty
		Input:
			address: Address to check if account is empty
		Output:
			True:  If account balance is empty
			False: If account balance is empty
		'''
		if self.AccountList[address]['Balance'] == 0:
			return True
		else:
			return False

	def AccountBalance(self, address):
		'''
		Returns account balance of address
		Input:
			address: Address to return account balance of
		Output:
			return balance of account address
		'''
		return self.AccountList[address]['Balance']


# x = AccountList()
# x.PopulateAccountList(10)
# print(x.AccountList)
# x.AddToBalance(0,10)
# print(x.AccountList)
# x.RemoveFromBalance(0,5)
# print(x.AccountList)
# print(x.ProcessTransaction(0,1,2.5151))
# print(x.AccountList)
# print(x.ProcessTransaction(0,1,2.5151))
# print(x.AccountList)
# print(x.MedianBlocksSolved())