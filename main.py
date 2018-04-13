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

# Create initial account list
masterAccountList = AccountList()
masterAccountList.PopulateAccountList(10, rand=True)
print(masterAccountList.AccountList)

# Initialize TransactionPool
transactionPool = TransactionPool(masterAccountList)

# Generate 100 valid transactions
transactionPool.GenerateValidTransactions(100)

# Generate 1% invalid transactions
#transactionPool.GeneratePercentInvalidTransactions(.01)

# Processes transactions
# for transaction in transactionPool.Transactions:
#	print(masterAccountList.ProcessTransaction(transaction))

# List of Masternodes
masterNodes = []

# Generate new nodes that contain blocks and process transactions
nodes = []
for userID in range(1,6):
	# Need to split the transaction pool
	# It may be that the split transaction pool is generating errors because
	# it was generated with the additional transactions in mind
	# Update this so the transactions in the pool are independently valid from eachother
	splitTransactionPool = SplitTransactions()
	newNode = Node(userID, copy.deepcopy(masterAccountList), copy.deepcopy(masterNodes), copy.deepcopy(splitTransactionPool))
	newNode = Node(userID, copy.deepcopy(masterAccountList), copy.deepcopy(masterNodes), copy.deepcopy(transactionPool.Transactions))
	nodes.append(newNode)

# need to ensure that transactions that do get processed get removed from transaction
# pool



#main.py
