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

def SplitTransactions():
	randomInt = random.randint(0,4)/5
	transactionStart = math.floor(randomInt * len(transactionPool.Transactions))
	transactionEnd = math.floor(randomInt+1 * len(transactionPool.Transactions))
	return transactionPool.Transactions[transactionStart:transactionEnd]

def BeginMasterNodeSelection():
	# After blocks are solved, attempts to initialize new masternodes
	for masterNode in masterNodes:
		threading.Thread(target=masterNode.MasternodeSelection).start()
		#masterNode.MasternodeSelection()


NumberOfAccounts = 100
MicroBlocksPerBlock = 3
MaxTimePerMicroBlock = 3

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
#transactionPool.GeneratePercentInvalidTransactions(.05)

# Processes transactions
# for transaction in transactionPool.Transactions:
#	print(masterAccountList.ProcessTransaction(transaction))

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
	# Splitting transaction pool
	# TODO: Update so the transaction splitting is based off of "location"
	splitTransactionPool = SplitTransactions()
	nodeBlocksSolved = masterAccountList.AccountList[userID]['NumberOfBlocksSolved']
	newNode = Node(userID, copy.deepcopy(masterAccountList), nodeBlocksSolved, copy.deepcopy(splitTransactionPool), MicroBlocksPerBlock, MaxTimePerMicroBlock)
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


#for node in nodes:
	#splitTransactionPool = SplitTransactions()
	#node.BeginBlockBuilding(splitTransactionPool)



for i in range(0,3):
	# Initialize TransactionPool
	transactionPool = TransactionPool(copy.deepcopy(masterNodes[0].ModifiedMasterAccountList))

	# Generate 100 valid transactions
	transactionPool.GenerateValidTransactions(math.floor(NumberOfAccounts/2))


	for node in nodes:
		splitTransactionPool = SplitTransactions()
		node.BeginBlockBuilding(splitTransactionPool)



# After all blocks are solved, beings master node selection process via threads
#AllBlocksSolved = Timer(25, BeginMasterNodeSelection)
#AllBlocksSolved.start()
	


#print(len(nodes))
	#for node in nodes:
	#	node.ForwardSolvedBlockToMasterNodes()







# need to ensure that transactions that do get processed get removed from transaction
# pool



