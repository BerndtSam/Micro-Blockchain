from AccountList import AccountList
from TransactionPool import TransactionPool
from Node import Node
import copy
import random
import math

def SplitTransactions():
	randomInt = random.randint(0,4)/5
	transactionStart = math.floor(randomInt * len(transactionPool.Transactions))
	transactionEnd = math.floor(randomInt+1 * len(transactionPool.Transactions))
	return transactionPool.Transactions[transactionStart:transactionEnd]

NumberOfAccounts = 100


# Create initial account list
masterAccountList = AccountList()
masterAccountList.PopulateAccountList(NumberOfAccounts, rand=True)
print(masterAccountList.AccountList)

# Initialize TransactionPool
transactionPool = TransactionPool(masterAccountList)

# Generate 100 valid transactions
transactionPool.GenerateValidTransactions(math.floor(NumberOfAccounts/2))
print('Transactions Generated')

# Generate 1% invalid transactions
#transactionPool.GeneratePercentInvalidTransactions(.01)

# Processes transactions
# for transaction in transactionPool.Transactions:
#	print(masterAccountList.ProcessTransaction(transaction))

# List of Masternodes
masterNodes = []

# Generate new nodes that contain blocks and process transactions
nodes = []
for userID in range(1,NumberOfAccounts+1):
	# Splitting transaction pool
	# TODO: Update so the transaction splitting is based off of "location"
	splitTransactionPool = SplitTransactions()
	newNode = Node(userID, copy.deepcopy(masterAccountList), copy.deepcopy(masterNodes), copy.deepcopy(splitTransactionPool))
	#newNode = Node(userID, copy.deepcopy(masterAccountList), copy.deepcopy(masterNodes), copy.deepcopy(transactionPool.Transactions))
	nodes.append(newNode)

# need to ensure that transactions that do get processed get removed from transaction
# pool



#main.py
