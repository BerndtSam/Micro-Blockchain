from AccountList import AccountList
from TransactionPool import TransactionPool
from Node import Node
from MasterNode import MasterNode
from threading import Timer
from Block import Block
import threading

import copy
import random
import math

def SplitTransactions(transaction_pool):
	randomInt = random.randint(0,2)/3
	transactionStart = math.floor(randomInt * len(transaction_pool.Transactions))
	transactionEnd = math.floor(randomInt+1 * len(transaction_pool.Transactions))
	return transaction_pool.Transactions[transactionStart:transactionEnd]


NumberOfAccounts = 100
MicroBlocksPerBlock = 3
MaxTimePerMicroBlock = 3
BlockIterations = 4

# Create initial account list
masterAccountList = AccountList()
masterAccountList.PopulateAccountList(NumberOfAccounts, rand=True)
print(masterAccountList.AccountList)

# Initialize TransactionPool
#transactionPool = TransactionPool(masterAccountList)

# Generate 100 valid transactions
#transactionPool.GenerateValidTransactions(math.floor(NumberOfAccounts/2))
#print('Transactions Generated')

# Generate 1% invalid transactions
#transactionPool.GeneratePercentInvalidTransactions(.05)

# List of Masternodes
masterNodes = []
for masterNodeID in range(0,math.floor(NumberOfAccounts/10)):
	tempTransactions = []
	nodeBlocksSolved = masterAccountList.AccountList[masterNodeID]['NumberOfBlocksSolved']
	tempMasterNode = MasterNode(masterNodeID, copy.deepcopy(masterAccountList), nodeBlocksSolved, MicroBlocksPerBlock, MaxTimePerMicroBlock, transactionPool=[], previousMasterNodeList=[])
	masterNodes.append(tempMasterNode)


# Generate new nodes that contain blocks and process transactions
nodes = []
for userID in range(0,NumberOfAccounts):
	nodeBlocksSolved = masterAccountList.AccountList[userID]['NumberOfBlocksSolved']
	newNode = Node(userID, copy.deepcopy(masterAccountList), nodeBlocksSolved, MicroBlocksPerBlock, MaxTimePerMicroBlock)
	#newNode = Node(userID, copy.deepcopy(masterAccountList), copy.deepcopy(masterNodes), copy.deepcopy(transactionPool.Transactions))
	nodes.append(newNode)


# Tells each masternode what the other masternode objects are
# Records the IDs of masternodes
masterNodeIDs = []
for masterNode in masterNodes:
	masterNode.SetMasterNodes(masterNodes)
	masterNodeIDs.append(masterNode.userID)

# Initially tells the nodes which are masternodes that they are masternodes (so they don't process transactions, etc.)
# Assigns the masternode list to nodes
for node in nodes:
	if node.userID in masterNodeIDs:
		node.SetMasterNode(True)
	node.SetMasterNodes(masterNodes)

# Tells each node what the other node objects are
for node in nodes:
	node.SetNodes(nodes)

# Tells masternodes what all the node objects are
for masterNode in masterNodes:
	masterNode.SetNodes(nodes)


# Main Program Loop
for i in range(0,BlockIterations):
	# Shuffles nodes to account for initialization time
	random.shuffle(nodes)

	# TODO: Update so the transaction splitting is based off of "location"

	# Initialize TransactionPool
	transactionPool = TransactionPool(copy.deepcopy(masterAccountList))

	# Generate 100 valid transactions
	#transactionPool.GenerateValidTransactions(math.floor(NumberOfAccounts/2))
	transactionPool.GenerateValidTransactions(math.floor(10))
	print('Transactions Generated')

	nodeThreads = []
	masterNodeThreads = []

	# Begins masternode processing incoming blocks
	for masterNode in masterNodes:
		masterNodeThread = threading.Thread(target=masterNode.ProcessIncomingBlocks)
		masterNodeThread.start()
		masterNodeThreads.append(masterNodeThread)

	# Begins node processing transactions and inserting into blocks
	for node in nodes:
		splitTransactionPool = SplitTransactions(copy.deepcopy(transactionPool))
		nodeThread = threading.Thread(target=node.BeginBlockBuilding, args=[copy.deepcopy(splitTransactionPool)])
		nodeThread.start()
		nodeThreads.append(nodeThread)

	# Joins all threads to get ready for next iteration
	for nodeThread in nodeThreads:
		nodeThread.join()
	for masterNodeThread in masterNodeThreads:
		masterNodeThread.join()

	masterAccountList.AccountList = copy.deepcopy(masterNodes[0].ModifiedMasterAccountList.AccountList)
	

	'''processed = 0
	unprocessed = 0

	for processedTransaction in processedTransactions:
		if processedTransaction.processed:
			processed += 1
		else:
			unprocessed += 1
	print("Total Processed Transactions: " + str(processed))
	print("Total Unprocessed Transactions: " + str(unprocessed))'''


	# Update each nodes account list
	for node in nodes:
		node.OriginalAccountList.AccountList = copy.deepcopy(masterAccountList.AccountList)
		node.ModifiedAccountList.AccountList = copy.deepcopy(masterAccountList.AccountList)
		node.ReinitializeNode()

	for masterNode in masterNodes:
		masterNode.ReinitializeMasterNode()





# need to ensure that transactions that do get processed get removed from transaction
# pool



