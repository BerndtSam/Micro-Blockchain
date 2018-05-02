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


def GenerateDistanceMatrix(numUsers):
	distanceMatrix = [[0 for x in range(numUsers+1)] for y in range(numUsers+1)] 
	for i in range(0,numUsers+1):
		for j in range(0,numUsers+1):
			if i == j:
				distanceMatrix[i][j] = 0
			else:
				distanceMatrix[i][j] = random.randint(1,10)
	return distanceMatrix

def AllocateTransactionsByDistance(userID, transactionPool, distanceMatrix, distanceThreshold):
	transactions = []
	for transaction in transactionPool.Transactions:
		if distanceMatrix[transaction.senderID][userID] <= distanceThreshold:
			transactions.append(transaction)
	return transactions






NumberOfAccounts = 100
MicroBlocksPerBlock = 3
MaxTimePerMicroBlock = 3
BlockIterations = 4
distanceThreshold = 3

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


DistanceMatrix = GenerateDistanceMatrix(NumberOfAccounts)
#print(DistanceMatrix)

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
	median = masterAccountList.MedianBlocksSolved()
	print('Median Blocks Solved: ' + str(masterAccountList.MedianBlocksSolved()))
	eligibleMasterNodes = [node for node in masterAccountList.AccountList if masterAccountList.AccountList[node]['NumberOfBlocksSolved'] > median] 
	print('Eligible MasterNodes: ' + str(eligibleMasterNodes))

	negativeBalancedNodes = [(node, masterAccountList.AccountList[node]['Balance']) for node in masterAccountList.AccountList if masterAccountList.AccountList[node]['Balance'] < 0] 
	print('Nodes with negative balances: ' + str(negativeBalancedNodes))

	# Shuffles nodes to account for initialization time
	random.shuffle(nodes)

	# TODO: Update so the transaction splitting is based off of "location"

	# Initialize TransactionPool
	transactionPool = TransactionPool(copy.deepcopy(masterAccountList))

	# Generate 100 valid transactions
	#transactionPool.GenerateValidTransactions(math.floor(NumberOfAccounts/2))
	transactionPool.GenerateValidTransactions(math.floor(10))
	print('Transactions Generated')
	for transaction in transactionPool.Transactions:
		print('From: ' + str(transaction.senderID) + ' To: ' + str(transaction.receiverID) + ' Coins: ' + str(transaction.coins))

	nodeThreads = []
	masterNodeThreads = []

	# Begins masternode processing incoming blocks
	for masterNode in masterNodes:
		masterNodeThread = threading.Thread(target=masterNode.ProcessIncomingBlocks)
		masterNodeThread.start()
		masterNodeThreads.append(masterNodeThread)

	# Begins node processing transactions and inserting into blocks
	for node in nodes:
		distanceTransactions = AllocateTransactionsByDistance(node.userID, transactionPool, DistanceMatrix, distanceThreshold)
		nodeThread = threading.Thread(target=node.BeginBlockBuilding, args=[distanceTransactions])
		nodeThread.start()
		nodeThreads.append(nodeThread)

	# Joins all threads to get ready for next iteration
	for nodeThread in nodeThreads:
		nodeThread.join()
	print("Joined all nodes")
	for masterNodeThread in masterNodeThreads:
		masterNodeThread.join()
	print("Joined all threads")

	print('\nStatistics:')
	print('Total Bytes Received Per MasterNode: ' + str(masterNodes[0].TotalBytesReceived))
	print('Total Bytes Sent Per MasterNode: ' + str(masterNodes[0].TotalBytesSent))
	print('Bytes Per Block Transmission from Node: ' + str(masterNodes[0].BytesPerBlockTransaction))
	print('Bytes Per Masternode Block Verification Transmission: ' + str(masterNodes[0].BytesPerMasterNodeBlockVerification))
	print('Bytes Per Census Verification Transmission: ' + str(masterNodes[0].BytesPerCensusVerification))
	print('Bytes to Compare and Verify Census: ' + str(masterNodes[0].BytesComparingCensus))
	print('Bytes Per Finalization of Account Lists Transmission: ' + str(masterNodes[0].BytesFinalizingAccountListTransmission))
	print('Bytes to Finalize Account List: ' + str(masterNodes[0].BytesFinalizingAccountLists))
	print('Bytes to Initialize new MasterNodes: ' + str(masterNodes[0].BytesMasterNodeSelection))

	masterAccountList.AccountList = copy.deepcopy(masterNodes[0].ModifiedMasterAccountList.AccountList)

	processed = 0
	unprocessed = 0

	for processedTransaction in transactionPool.Transactions:
		if processedTransaction.processed:
			processed += 1
		else:
			unprocessed += 1
	print("Total Processed Transactions: " + str(processed))
	print("Total Unprocessed Transactions: " + str(unprocessed))


	# Update each nodes account list
	for node in nodes:
		node.OriginalAccountList.AccountList = copy.deepcopy(masterAccountList.AccountList)
		node.ModifiedAccountList.AccountList = copy.deepcopy(masterAccountList.AccountList)
		node.ReinitializeNode()

	for masterNode in masterNodes:
		masterNode.ReinitializeMasterNode()





# need to ensure that transactions that do get processed get removed from transaction
# pool



