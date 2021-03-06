from AccountList import AccountList
from TransactionPool import TransactionPool
from Node import Node
from MasterNode import MasterNode
from threading import Timer
from Block import Block
import threading
import time

import copy
import random
import math

def GenerateDistanceMatrix(numUsers):
	''' 
	Generates a distance matrix indicating the physical latency between nodes
	'''
	distanceMatrix = [[0 for x in range(numUsers+1)] for y in range(numUsers+1)] 
	for i in range(0,numUsers+1):
		for j in range(0,numUsers+1):
			if i == j:
				distanceMatrix[i][j] = 0
			else:
				distanceMatrix[i][j] = random.randint(1,10)
				distanceMatrix[j][i] = distanceMatrix[i][j]
	return distanceMatrix

def AllocateTransactionsByDistance(userID, transactionPool, distanceMatrix, distanceThreshold):
	'''
	Allocates the transactions given a transaction pool to a given node based off of the distance threshold and distance
	between nodes
	Input:
		userID: Node to allocate transactions for
		transactionPool: All transactions
		distanceMatrix: Distance between each of the nodes
		distanceThreshold: Maximum distance a transaction can travel in terms of nodes
	Output:
		transactions: Transactions for a node by filtering via distance matrix
	'''
	transactions = []
	for transaction in transactionPool.Transactions:
		if distanceMatrix[transaction.senderID][userID] <= distanceThreshold:
			transactions.append(transaction)
	return transactions



NumberOfAccounts = 100
MicroBlocksPerBlock = 5
MaxTimePerMicroBlock = 3
BlockIterations = 10
DistanceThreshold = 4
NumberOfTransactionsPerIteration = 50
NumberOfMasterNodes = 10

if NumberOfTransactionsPerIteration > NumberOfAccounts:
	assert(NumberOfAccounts >= NumberOfTransactionsPerIteration)
	print("Invalid number of transactions per iteration. The number of transactions must not exceed the number of accounts")

# Create initial account list
masterAccountList = AccountList()
masterAccountList.PopulateAccountList(NumberOfAccounts, rand=True)
print(masterAccountList.AccountList)

# List of Masternodes
masterNodes = []
for masterNodeID in range(0,NumberOfMasterNodes):
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

# Roll over transactions from previous iteration
UnprocessedTransactions = []

# Initialize TransactionPool
transactionPool = TransactionPool(copy.deepcopy(masterAccountList))

sentOverheadInfo = []
receivedOverheadInfo = []
TransactionsProcessedInfo = []
TransactionsUnprocessedInfo = []
TimeInfo = []

# Main Program Loop
for i in range(0,BlockIterations):
	beginTime = time.time()
	print('Iteration: ' + str(i))

	median = masterAccountList.MedianBlocksSolved()
	print('Median Blocks Solved: ' + str(masterAccountList.MedianBlocksSolved()))
	eligibleMasterNodes = [node for node in masterAccountList.AccountList if masterAccountList.AccountList[node]['NumberOfBlocksSolved'] > median] 
	print('Eligible MasterNodes: ' + str(eligibleMasterNodes))

	negativeBalancedNodes = [(node, masterAccountList.AccountList[node]['Balance']) for node in masterAccountList.AccountList if masterAccountList.AccountList[node]['Balance'] < 0] 
	print('Nodes with negative balances: ' + str(negativeBalancedNodes))

	# Shuffles nodes to account for initialization time
	random.shuffle(nodes)

	# Renitialize TransactionPool
	transactionPool.ReinitializeTransactionPool(copy.deepcopy(masterAccountList), UnprocessedTransactions)

	# Generate valid transactions
	transactionPool.GenerateValidTransactions(NumberOfTransactionsPerIteration, UnprocessedTransactions)

	# TODO: Generate 1% invalid transactions
	#transactionPool.GeneratePercentInvalidTransactions(.01)
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
		distanceTransactions = AllocateTransactionsByDistance(node.userID, transactionPool, DistanceMatrix, DistanceThreshold)
		nodeThread = threading.Thread(target=node.BeginBlockBuilding, args=[distanceTransactions])
		nodeThread.start()
		nodeThreads.append(nodeThread)


	# Joins all threads to get ready for next iteration
	for nodeThread in nodeThreads:
		nodeThread.join(3)
	print("Joined all node threads")
	for masterNodeThread in masterNodeThreads:
		masterNodeThread.join()
	print("Joined all masternode threads")
	

	AverageMasterNodeOverheadSent = 0
	AverageMasterNodeOverheadReceived = 0
	for masterNode in masterNodes:
		AverageMasterNodeOverheadSent += masterNode.TotalBytesSent
		AverageMasterNodeOverheadReceived += masterNode.TotalBytesReceived
	AverageMasterNodeOverheadReceived = AverageMasterNodeOverheadReceived / len(masterNodes)
	AverageMasterNodeOverheadSent = AverageMasterNodeOverheadSent / len(masterNodes)

	print('\nStatistics:')
	print('Average Bytes Received Per MasterNode: ' + str(masterNodes[0].TotalBytesReceived))
	print('Average Bytes Sent Per MasterNode: ' + str(masterNodes[0].TotalBytesSent))
	print('Bytes Per Block Transmission from Node: ' + str(masterNodes[0].BytesPerBlockTransaction))
	print('Bytes Per Masternode Block Verification Transmission: ' + str(masterNodes[0].BytesPerMasterNodeBlockVerification))
	print('Bytes Per Census Verification Transmission: ' + str(masterNodes[0].BytesPerCensusVerification))
	print('Bytes to Compare and Verify Census: ' + str(masterNodes[0].BytesComparingCensus))
	print('Bytes Per Finalization of Account Lists Transmission: ' + str(masterNodes[0].BytesFinalizingAccountListTransmission))
	print('Bytes to Finalize Account List: ' + str(masterNodes[0].BytesFinalizingAccountLists))
	print('Bytes to Initialize new MasterNodes: ' + str(masterNodes[0].BytesMasterNodeSelection))

	processed = 0
	unprocessed = 0
	UnprocessedTransactions = []
	for transaction in transactionPool.Transactions:
		if transaction.processed:
			processed += 1
		else:
			unprocessed += 1
			UnprocessedTransactions.append(transaction)
	print("Total Processed Transactions: " + str(processed))
	print("Total Unprocessed Transactions: " + str(unprocessed))
	print('Unprocessed Transactions: ' + str(UnprocessedTransactions))

	sentOverheadInfo.append(AverageMasterNodeOverheadSent)
	receivedOverheadInfo.append(AverageMasterNodeOverheadReceived)
	TransactionsProcessedInfo.append(processed)
	TransactionsUnprocessedInfo.append(unprocessed)
	TimeInfo.append(time.time() - beginTime)


	masterAccountList.AccountList = copy.deepcopy(masterNodes[0].ModifiedMasterAccountList.AccountList)


	# Update each nodes account list
	# Reinitialize all nodes
	for node in nodes:
		node.OriginalAccountList.AccountList = copy.deepcopy(masterAccountList.AccountList)
		node.ModifiedAccountList.AccountList = copy.deepcopy(masterAccountList.AccountList)
		node.ReinitializeNode()
	# Reinitialize all MasterNodes
	for masterNode in masterNodes:
		masterNode.ReinitializeMasterNode()

print('Sent Overhead ' + str(sentOverheadInfo))
print('Received Overhead ' + str(receivedOverheadInfo))
print('Processed Transactions ' + str(TransactionsProcessedInfo))
print('Unprocessed Transactions ' + str(TransactionsUnprocessedInfo))
print('Time per Iteration ' + str(TimeInfo))

