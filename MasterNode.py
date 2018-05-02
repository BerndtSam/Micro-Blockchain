from Node import Node
from threading import Timer
import threading
import random
import copy
import math
import sys

class MasterNode(Node):
	def __init__(self, userID, accountList, blocksSolved, microBlocksPerBlock, maxTimePerMicroBlock, transactionPool, previousMasterNodeList):
		super(MasterNode, self).__init__(userID, accountList, blocksSolved, microBlocksPerBlock, maxTimePerMicroBlock)
		super(MasterNode, self).SetMasterNode(True)
		
		self.OriginalMasterAccountList = copy.deepcopy(accountList)
		self.ModifiedMasterAccountList = copy.deepcopy(accountList)

		self.PreviousMasterNodeList = previousMasterNodeList
		self.ReplacementMasterNode = None
		self.SelectedMasterNodes = []
		self.CurrentMasterNodeIDs = []
		
		self.SelfVerifiedBlocks = []
		self.VerifiedBlocks = []
		self.VerifiedBlockCount = {}

		self.ProcessedTransactions = []

		self.Census = None
		self.CensusComplete = False
		self.CensusInitiated = False
		self.CensusVerified = False
		self.CensusMergeComplete = False
		self.VerifiedCensus = []

		self.AddBlockLock = threading.Lock()
		self.VerifiedBlockLock = threading.Lock()
		self.SelfVerifiedBlockLock = threading.Lock()
		self.SelfVerificationLock = threading.Lock()
		
		self.BlocksReady = 0;
		self.CensusReady = 0;
		
		self.BlocksToVerify = []
		self.OriginalAccountListsToVerify = []
		self.ModifiedAccountListsToVerify = []

		self.BytesPerBlockTransaction = 0
		self.BytesPerMasterNodeBlockVerification = 0
		self.BytesPerCensusVerification = 0
		self.BytesFinalizingAccountLists = 0
		self.BytesComparingCensus = 0
		self.BytesFinalizingAccountListTransmission = 0
		self.BytesMasterNodeSelection = 0
		self.TotalBytesSent = 0
		self.TotalBytesReceived = 0
		self.HTTPHeaderSize = 800


	def SetCurrentMasterNodeIDs(self):
		'''
		Gathers the masternode IDs so that they are not selected as future masternodes
		'''
		self.CurrentMasterNodeIDs = []
		for masterNode in self.MasterNodes:
			self.CurrentMasterNodeIDs.append(masterNode.userID)

	def SelectReplacementMasterNode(self):
		'''
		Selects the next replacement MasterNode. Ensures it has not been added to selected
		MasterNodes already
		'''
		# Sets Current MasterNode IDs so that they won't be considered for future master nodes
		self.SetCurrentMasterNodeIDs()

		# Goes through account list, determines what nodes have greater than the median number of blocks solved
		# and if those nodes also are not in the previous masternodes list. If both conditions are satisifed,
		# randomly chooses a replacement masternode
		AvailableMasterNodes = [Node for Node in self.OriginalMasterAccountList.AccountList if self.OriginalMasterAccountList.AccountList[Node]['NumberOfBlocksSolved'] >= self.OriginalMasterAccountList.MedianBlocksSolved() and Node not in self.PreviousMasterNodeList and Node not in self.CurrentMasterNodeIDs]
		self.ReplacementMasterNode = AvailableMasterNodes[random.randint(0,len(AvailableMasterNodes)-1)]

		MasterNodeExists = False
		for masterNode in self.MasterNodes:
			# Checks if another masternode already has the randomly choosen masternode as part of its list
			# if below returns false, it means it has
			self.TotalBytesSent += sys.getsizeof(self.ReplacementMasterNode) + self.HTTPHeaderSize
			self.BytesMasterNodeSelection += sys.getsizeof(self.ReplacementMasterNode) + self.HTTPHeaderSize
			if masterNode.CompareNewMasterNodes(self.ReplacementMasterNode) == False:
				print("MasterNodeID: " + str(self.userID) + " has attempted to set a masternode which already has been chosen: " + str(self.ReplacementMasterNode))
				print(self.CurrentMasterNodeIDs)
				print(self.PreviousMasterNodeList)
				MasterNodeExists = True
				break

		# If the masternode has already been chosen
		if MasterNodeExists == True:
			self.SelectReplacementMasterNode()
		else:
			print("MasterNode: " + str(self.userID) + " is adding masternode: " + str(self.ReplacementMasterNode) + " as a replacement Masternode")
			# If it hasn't, lets all the other masternodes know to add it to their list
			for masterNode in self.MasterNodes:
				masterNode.AddSelectedMasterNode(self.ReplacementMasterNode)
				self.TotalBytesSent += sys.getsizeof(self.ReplacementMasterNode) + self.HTTPHeaderSize
				self.BytesMasterNodeSelection += sys.getsizeof(self.ReplacementMasterNode) + self.HTTPHeaderSize


	def MasternodeSelection(self):
		'''
		Handles the entire masternode selection process
		# Selection happens after end of block iteration
		# User must have greater or equal to the median number of blocks solved to be masternode
		# Receives accountlist, new masternode list
		# Sends announce to each node saying its the new masternode
		# Send account list to each masternode and does quorum to verify
		#TODO: If masternode does not have same accountlist, gets dropped
		#TODO: Must ping every 15 seconds
		#TODO: must respond to pings

		'''
		# Selects replacement masternodes in threaded process
		self.SelectReplacementMasterNode()
		# While it hasn't received a new masternode from the other masternodes, waits
		while len(self.SelectedMasterNodes) != len(self.MasterNodes):
			continue
		# Initializes the new masternodes once all new masternodes selected
		self.InitializeNewMasterNode()
		# Returns to end thread
		return


	def CompareNewMasterNodes(self, masterNodeID):
		'''
		Compares the userIDs of another masternodes selected masternode to the userIDs of already selected new masternodes given to this masternode
		Input:
			masterNodeID: userID of masternode to compare
		Output:
			True: If masterNodeID is not already in the selected masternodes
			False: If masterNodeID is already in the selected masternodes
		'''
		self.TotalBytesReceived += sys.getsizeof(masterNodeID) + self.HTTPHeaderSize
		if masterNodeID in self.SelectedMasterNodes:
			return False
		return True

	def AddSelectedMasterNode(self, masterNodeID):
		'''
		Adds a selected masternode ID to a list of masternodeID's that have been selected to replace the current masternodes
		Input:
			masterNodeID: ID of masternode to be added to replace current masternodes
		'''
		self.TotalBytesReceived += sys.getsizeof(masterNodeID) + self.HTTPHeaderSize
		self.SelectedMasterNodes.append(masterNodeID)

	def InitializeNewMasterNode(self):
		'''
		Initializes the new masternode after selection
		'''
		for node in self.Nodes:
			# Sets this node to be a regular node again
			if node.userID == self.userID:
				node.SetMasterNode(False)
				print("MasterNodeID: " + str(self.userID) + " is relinquishing its control as a MasterNode to: " + str(self.ReplacementMasterNode))
				break
			node.SetReset(True)
			# Gives each node the new master account list
			#node.OriginalAccountList.AccountList = copy.deepcopy(self.ModifiedMasterAccountList.AccountList)
			#node.ModifiedAccountList.AccountList = copy.deepcopy(self.ModifiedMasterAccountList.AccountList)

		for node in self.Nodes:
			# Sets new masternode variables up
			if node.userID == self.ReplacementMasterNode:
				node.SetMasterNode(True)

				# Update Node class properties to "Change" the masternode
				self.userID = node.userID
				self.BlocksSolved = node.BlocksSolved
				self.OriginalMasterAccountList.AccountList = copy.deepcopy(self.ModifiedMasterAccountList.AccountList)
				self.ModifiedMasterAccountList.AccountList = copy.deepcopy(self.ModifiedMasterAccountList.AccountList)
				self.BytesMasterNodeSelection += sys.getsizeof(self.ModifiedMasterAccountList.AccountList) + sys.getsizeof(self.MasterNodes)
				self.TotalBytesSent += sys.getsizeof(self.ModifiedMasterAccountList.AccountList) + sys.getsizeof(self.MasterNodes)
				print("MasterNodeID: " + str(self.userID) + " initialized as a new MasterNode")
				break


	def ReinitializeMasterNode(self):
		# Reinitialize this MasterNode's masternode class variables
		self.SelectedMasterNodes = []
		self.ReplacementMasterNode = None
		# Ensures the current masternodes can't submit a block
		self.PreviousMasterNodeList = []
		for masterNode in self.MasterNodes:
			self.PreviousMasterNodeList.append(masterNode.userID)

		self.SelfVerifiedBlocks = []
		self.VerifiedBlocks = []
		self.VerifiedBlockCount = {}
		self.Census = None
		self.CensusComplete = False
		self.CensusInitiated = False
		self.CensusVerified = False
		self.CensusMergeComplete = False
		self.VerifiedCensus = []

		self.BlocksReady = 0;
		self.CensusReady = 0;

		self.BlocksToVerify = []
		self.OriginalAccountListsToVerify = []
		self.ModifiedAccountListsToVerify = []

		self.ProcessedTransactions = []


	def ReceiveIncomingBlocks(self, block, originalAccountList, modifiedAccountList):
		'''
		Nodes will call this function to have the masternode begin processing the blocks. 
		Ends the nodes which calls this function's thread.
		Input:
			block: Block to process
			originalAccountList: Original Account List to verify
			modifiedAccountList: Modified Account List to verify
		'''
		#print('User sending block: ' + str(block.BlockID))
		self.AddBlockLock.acquire()
		self.BlocksToVerify.append(block)
		self.OriginalAccountListsToVerify.append(originalAccountList)
		self.ModifiedAccountListsToVerify.append(modifiedAccountList)
		self.BytesPerBlockTransaction = sys.getsizeof(block) + sys.getsizeof(block.MicroBlocks) + len(self.BlocksToVerify[0].MicroBlocks)*sys.getsizeof(block.MicroBlocks[0].TransactionList) + sys.getsizeof(originalAccountList) + sys.getsizeof(originalAccountList.AccountList) + sys.getsizeof(modifiedAccountList) + sys.getsizeof(modifiedAccountList.AccountList) + self.HTTPHeaderSize
		self.TotalBytesReceived += sys.getsizeof(block) + sys.getsizeof(block.MicroBlocks) + len(self.BlocksToVerify[0].MicroBlocks)*sys.getsizeof(block.MicroBlocks[0].TransactionList) + sys.getsizeof(originalAccountList) + sys.getsizeof(originalAccountList.AccountList) + sys.getsizeof(modifiedAccountList) + sys.getsizeof(modifiedAccountList.AccountList) + self.HTTPHeaderSize
		self.AddBlockLock.release()


	def ProcessIncomingBlocks(self):
		'''
		If a node solves a block, it will update the BlocksToVerify * list, which will be iterated in
		this function. This function will then loop through and verify the blocks first, and then
		with the other masternodes. If 5 blocks are verified, begins census
		'''

		# Have this loop to go through received blocks and process them. Add to verified blocks if need be
		while len(self.VerifiedBlocks) < 5 and self.CensusInitiated == False:
			for i in range(0,len(self.BlocksToVerify)):
				# Verifies the block information is valid
				if self.VerifyBlock(self.BlocksToVerify[i], self.OriginalAccountListsToVerify[i], self.ModifiedAccountListsToVerify[i]):
					for masterNode in self.MasterNodes:
						# Send block to each masternode to verify
						masterNode.VerifyBlockFromMasterNode(self.BlocksToVerify[i], self.OriginalAccountListsToVerify[i], self.ModifiedAccountListsToVerify[i])
						self.BytesPerMasterNodeBlockVerification = sys.getsizeof(self.BlocksToVerify[i]) + sys.getsizeof(self.BlocksToVerify[i].MicroBlocks) + len(self.BlocksToVerify[i].MicroBlocks)*sys.getsizeof(self.BlocksToVerify[i].MicroBlocks[0].TransactionList) + sys.getsizeof(self.OriginalAccountListsToVerify[i]) + sys.getsizeof(self.ModifiedAccountListsToVerify[i]) + self.HTTPHeaderSize
						self.TotalBytesSent += sys.getsizeof(self.BlocksToVerify[i]) + sys.getsizeof(self.BlocksToVerify[i].MicroBlocks) + len(self.BlocksToVerify[i].MicroBlocks)*sys.getsizeof(self.BlocksToVerify[i].MicroBlocks[0].TransactionList) + sys.getsizeof(self.OriginalAccountListsToVerify[i]) + sys.getsizeof(self.ModifiedAccountListsToVerify[i]) + self.HTTPHeaderSize
				# Pops off the just verified/unverified block
				self.BlocksToVerify.pop(0)
				self.OriginalAccountListsToVerify.pop(0)
				self.ModifiedAccountListsToVerify.pop(0)
				break
		
		# Print out the verified block list for each masternode
		verifiedBlockList = [block.BlockID for block in self.VerifiedBlocks]
		print('MasterNode ' + str(self.userID) + ' Verified Blocks' + str(verifiedBlockList))

		self.CensusInitiated = True

		# Need to increment the block count for blocks who solved


		# Wait up for masternodes
		for masterNode in self.MasterNodes:
			masterNode.ReadyUpBlocks()
			self.TotalBytesSent += self.HTTPHeaderSize

		while self.BlocksReady < len(self.MasterNodes):
			continue

		self.BlocksToVerify = []
		self.OriginalAccountListsToVerify = []
		self.ModifiedAccountListsToVerify = []

		# Once all masternodes ready, initiate census
		self.InitiateCensus()


	def ReadyUpBlocks(self):
		'''
		Increments the BlocksReady count which indicates the number of masternodes who are ready for census
		'''
		self.BlocksReady += 1
		self.TotalBytesReceived += self.HTTPHeaderSize

	def ReadyUpCensus(self):
		'''
		Increments the CensusReady count which indicates the number of masternodes who are ready 
		to compare census
		'''
		self.CensusReady += 1
		self.TotalBytesReceived += self.HTTPHeaderSize


	def VerifyBlockFromMasterNode(self, block, originalAccountList, modifiedAccountList):
		'''
		If a masternode receives a valid block, it will send it to the other masternodes via this function
		Will increment the count for the specified block if valid, voting that it is good
		Input:
			block: Solved block
			originalAccountList: Original account list to verify against
			modifiedAccountList: Account list after transactions to verify against
		Output:
			True: If block is valid
			False: If block is not valid
		'''
		self.SelfVerifiedBlockLock.acquire()
		self.TotalBytesReceived += sys.getsizeof(block) + sys.getsizeof(block.MicroBlocks) + len(block.MicroBlocks)*sys.getsizeof(block.MicroBlocks[0].TransactionList) + sys.getsizeof(originalAccountList) + sys.getsizeof(originalAccountList.AccountList) + sys.getsizeof(modifiedAccountList) + sys.getsizeof(modifiedAccountList.AccountList)
		if block not in self.SelfVerifiedBlocks:
			if self.VerifyBlock(block, originalAccountList, modifiedAccountList):
				self.SelfVerifiedBlocks.append(block)
				self.VerifiedBlockCount[block.BlockID] = 1
				self.SelfVerifiedBlockLock.release()
				return True
			else:
				self.SelfVerifiedBlockLock.release()
				return False
		else:
			self.SelfVerifiedBlockLock.release()
			self.VerifiedBlockLock.acquire()
			self.VerifiedBlockCount[block.BlockID] += 1
			if self.VerifiedBlockCount[block.BlockID] >= self.Quorum() and len(self.VerifiedBlocks) < 5:
				self.AddToVerifiedBlockList(block)
			self.VerifiedBlockLock.release()
			return True


	def InitiateCensus(self):
		'''
		Once all masternodes agree on the verified blocks, census gets initiated
		This masternode will complete the census, and then will have all other masternodes complete the census
		After all masternodes have completed the census, compares against eachother
		'''
		print('Census Initiated by: ' + str(self.userID))

		# Performs the Census
		self.PerformCensus()

		# Wait for masternodes to complete census
		for masterNode in self.MasterNodes:
			masterNode.ReadyUpCensus()
			self.TotalBytesSent += self.HTTPHeaderSize

		while self.CensusReady < len(self.MasterNodes):
			continue
		
		# Compares census between masternodes
		for masterNode in self.MasterNodes:
			masterNode.CompareCensus(self.userID, self.Census)
			self.TotalBytesSent += sys.getsizeof(self.userID) + sys.getsizeof(self.Census) + self.HTTPHeaderSize
			self.BytesPerCensusVerification = sys.getsizeof(self.userID) + sys.getsizeof(self.Census) + self.HTTPHeaderSize
			self.BytesComparingCensus += sys.getsizeof(self.userID) + sys.getsizeof(self.Census) + self.HTTPHeaderSize
		# Waits for census comparison to be complete
		while not self.CensusVerified:
			continue

		self.InitiateFinalAccountListMerge()

	def InitiateFinalAccountListMerge(self):
		'''
		Merges the census into the account list, then compares account list to rest of masternodes
		'''
		# Verifies that the rest of the masternodes have completed their census
		mergeReady = 0
		masterNodesReady = []
		while mergeReady != len(self.MasterNodes):
			mergeReady = 0
			for masterNode in self.MasterNodes:
				if masterNode.CensusComplete == True:
					mergeReady += 1
				if masterNode.userID not in masterNodesReady and masterNode.CensusComplete == True:
					self.TotalBytesReceived += self.HTTPHeaderSize
					self.BytesComparingCensus += self.HTTPHeaderSize
					masterNodesReady.append(masterNode.userID)
		self.MergeCensusIntoAccountList()

		# Verifies that the rest of the masternodes have merged their census into account list
		mergeReady = 0
		masterNodesReady = []
		while mergeReady != len(self.MasterNodes):
			mergeReady = 0
			for masterNode in self.MasterNodes:
				if masterNode.CensusMergeComplete == True:
					self.TotalBytesReceived += self.HTTPHeaderSize
					self.BytesComparingCensus += self.HTTPHeaderSize
					mergeReady += 1
				if masterNode.userID not in masterNodesReady and masterNode.CensusMergeComplete == True:
					self.TotalBytesReceived += self.HTTPHeaderSize
					self.BytesComparingCensus += self.HTTPHeaderSize
					masterNodesReady.append(masterNode.userID)

		self.FinalizeAccountList()


	def CompareCensus(self, masterNodeID, census):
		'''
		Compares this masternodes census against another masternodes census.
		Input:
			masterNodeID: ID of masternode the census was received from
			census: Census from masternode to compare against own
		'''
		self.TotalBytesReceived += sys.getsizeof(masterNodeID) + sys.getsizeof(census) + self.HTTPHeaderSize
		self.BytesComparingCensus += sys.getsizeof(masterNodeID) + sys.getsizeof(census) + self.HTTPHeaderSize
		valid = True

		# Validates that the census values are valid
		for userid in census:
			if census[userid]['Balance'] != self.Census[userid]['Balance']:
				print("Invalid census received from Masternode: " + str(masterNodeID))
				valid = False
				break

		if valid == True:
			self.VerifiedCensus.append(masterNodeID)
		else:
			# TODO: Need to initiate a new masternode and remove this one from the remainder of the process
			pass

		if len(self.VerifiedCensus) > self.Quorum():
			#print('Census validated by:' + str(self.userID))
			self.CensusVerified = True


	def PerformCensus(self):
		'''
		Performs the census if it hasn't already been completed by going through the verified blocks
		and adding up all additions and subtractions from receivers and senders respectively
		Removes duplicate transactions
		Increments number of blocks solved for the census
		'''
		if not self.CensusComplete:
			processedTransactions = []
			processedTransactionSenders = []
			self.Census = self.OriginalMasterAccountList.EmptyAccountList()
			for block in self.VerifiedBlocks:
				for microblock in block.MicroBlocks:
					for transaction in microblock.TransactionList:
						# Ensures no duplicates
						if transaction not in processedTransactions and transaction.senderID not in processedTransactionSenders:
								transaction.processed = True
								processedTransactions.append(copy.deepcopy(transaction))
								processedTransactionSenders.append(transaction.senderID)
								self.Census[transaction.senderID]['Balance'] -= transaction.coins
								self.Census[transaction.receiverID]['Balance'] += transaction.coins
				# Increment number of blocks solved for each block
				self.ModifiedMasterAccountList.AddBlock(block.BlockID)
			self.CensusComplete = True

	def AddToVerifiedBlockList(self, block):
		'''
		Adds block to the verified block list, after checking to make sure it is eligible
		Input:
			block: Block to add to list
		'''
		# If the block has not already been verified and if there is less than the maximum amount of verified blocks
		if block not in self.VerifiedBlocks and len(self.VerifiedBlocks) < 5:
			# Appends to verified block list
			self.VerifiedBlocks.append(block)

			print("Block: " + str(block.BlockID) + " verified by MasterNode: " + str(self.userID))


	def Quorum(self):
		'''
		Calculates quorum for the masternodes
		'''
		return math.ceil(len(self.MasterNodes)/2)
			

	def VerifyBlock(self, block, originalAccountList, modifiedAccountList):
		'''
		Verifies the block, original account list, and modified account list given from a node
		Input:
			block: Block with microblocks to verify transactions from
			originalAccountList: original account list to verify against masternodes original account list
			modifiedAccountList: modified account list to verify against masternodes modified account list
		'''
		# Verifies original account list is the same
		for userid in originalAccountList.AccountList:
			if self.OriginalMasterAccountList.AccountList[userid] != originalAccountList.AccountList[userid]:
				print("Invalid Account List")
				return False

		# Verifies Transactions
		TestAccountList = copy.deepcopy(self.OriginalMasterAccountList)
		# Iterates through the microblocks in the block
		for microBlock in block.MicroBlocks:
			# Iterates through the transactions in the microblock
			for transaction in microBlock.TransactionList:
				# Verifies each transaction, notifies if invalid transaction
				if not TestAccountList.ProcessTransaction(transaction):
					print("Invalid Transaction detected by MasterNode: " + str(self.userID) + " in block sent by node: " + str(block.BlockID))
					print(transaction.coins)
					print(transaction.senderID)
					print(self.OriginalMasterAccountList.AccountList[transaction.senderID])
					return False
		
		# Verifies that the changes to the account list are accurate by comparing
		# the test account list to the given modified account list
		for userid in modifiedAccountList.AccountList:
			if TestAccountList.AccountList[userid] != modifiedAccountList.AccountList[userid]:
				print("MasterNode: " + str(self.userID) + " detected invalid modified account list from node: " + str(block.BlockID))
				return False

		return True


	def MergeCensusIntoAccountList(self):
		'''
		Merge the now verified census into the account list
		'''
		# For each user id in the census, adds the value of the census to the account list
		for userid in self.Census:
			self.ModifiedMasterAccountList.AccountList[userid]['Balance'] += self.Census[userid]['Balance']
		print('MasterNode: ' + str(self.userID) + ' has merged the census')
		self.CensusMergeComplete = True

	def FinalizeAccountList(self):
		'''
		Verifies all the values in the now modified account list are valid. If so, starts the masternode 
		selection process
		'''
		for masterNode in self.MasterNodes:
			self.TotalBytesSent += self.HTTPHeaderSize + sys.getsizeof(self.ModifiedMasterAccountList) + sys.getsizeof(self.ModifiedMasterAccountList.AccountList)
			self.TotalBytesReceived += self.HTTPHeaderSize + sys.getsizeof(self.ModifiedMasterAccountList) + sys.getsizeof(self.ModifiedMasterAccountList.AccountList)
			self.BytesFinalizingAccountLists += self.HTTPHeaderSize + sys.getsizeof(self.ModifiedMasterAccountList) + sys.getsizeof(self.ModifiedMasterAccountList.AccountList)
			self.BytesFinalizingAccountListTransmission = self.HTTPHeaderSize + sys.getsizeof(self.ModifiedMasterAccountList) + sys.getsizeof(self.ModifiedMasterAccountList.AccountList)
			for userid in masterNode.ModifiedMasterAccountList.AccountList:
				if masterNode.ModifiedMasterAccountList.AccountList[userid] != self.ModifiedMasterAccountList.AccountList[userid]:
					print('Masternode ' + str(self.userID) + 'has detected a flaw in the account list of Masternode ' + str(masterNode.userID))
					#TODO: Add failure case (remove masternode from this iteration)

		print('Account List Verified for Masternode ' + str(self.userID))
		Timer(10, self.MasternodeSelection())
		#self.MasternodeSelection()

	# Quorum proceedure for accountlist ot define master accountlist

