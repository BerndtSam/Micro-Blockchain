from Node import Node
from threading import Timer
import random
import copy
import math

class MasterNode(Node):
	def __init__(self, userID, accountList, blocksSolved, microBlocksPerBlock, maxTimePerMicroBlock, transactionPool, previousMasterNodeList):
		super(MasterNode, self).__init__(userID, accountList, blocksSolved, transactionPool, microBlocksPerBlock, maxTimePerMicroBlock)
		super(MasterNode, self).SetMasterNode(True)
		self.PreviousMasterNodeList = previousMasterNodeList
		self.ReplacementMasterNode = None
		self.SelectedMasterNodes = []
		self.CurrentMasterNodeIDs = []
		self.SelfVerifiedBlocks = []
		self.VerifiedBlocks = []
		self.VerifiedBlockCount = {}
		self.OriginalMasterAccountList = copy.deepcopy(accountList)
		self.ModifiedMasterAccountList = copy.deepcopy(accountList)
		self.Census = None
		self.CensusComplete = False
		self.CensusInitiated = False
		self.CensusVerified = False
		self.CensusMergeComplete = False
		self.VerifiedCensus = []


	def SetCurrentMasterNodeIDs(self):
		'''
		Gathers the masternode IDs so that they are not selected as future masternodes
		'''
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
			if masterNode.CompareNewMasterNodes(self.ReplacementMasterNode) == False:
				print("MasterNodeID: " + str(self.userID) + " has attempted to set a masternode which already has been chosen: " + str(self.ReplacementMasterNode))
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
		if masterNodeID in self.SelectedMasterNodes:
			return False
		return True

	def AddSelectedMasterNode(self, masterNodeID):
		'''
		Adds a selected masternode ID to a list of masternodeID's that have been selected to replace the current masternodes
		Input:
			masterNodeID: ID of masternode to be added to replace current masternodes
		'''
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

		for node in self.Nodes:
			# Sets new masternode variables up
			if node.userID == self.ReplacementMasterNode:
				node.SetMasterNode(True)

				# Reinitialize this MasterNode's masternode class variables
				self.SelectedMasterNodes = []
				self.ReplacementMasterNode = None
				# Ensures the current masternodes can't submit a block
				self.PreviousMasterNodeList = []
				for masterNode in self.MasterNodes:
					self.PreviousMasterNodeList.append(masterNode.userID)


				# Update Node class properties to "Change" the masternode
				self.userID = node.userID
				self.BlocksSolved = node.BlocksSolved
				self.OriginalMasterAccountList = copy.deepcopy(self.ModifiedMasterAccountList)
				self.ModifiedMasterAccountList = copy.deepcopy(self.ModifiedMasterAccountList)


				self.SelfVerifiedBlocks = []
				self.VerifiedBlocks = []
				self.VerifiedBlockCount = {}
				self.Census = None
				self.CensusComplete = False
				self.CensusInitiated = False
				self.CensusVerified = False
				self.CensusMergeComplete = False
				self.VerifiedCensus = []


				print("MasterNodeID: " + str(self.userID) + " initialized as a new MasterNode")
				break

	def ProcessIncomingBlocks(self, block, originalAccountList, modifiedAccountList):
		'''
		If a node solves a block, it is sent to this function for the masternode to verify
		MasterNode will verify the block itself, then send it to the other masternodes to verify
		Input:
			block: Solved block
			originalAccountList: Original account list to verify against
			modifiedAccountList: Account list after transactions to verify against
		'''
		# If the masternode has not yet accepted 5 blocks
		if len(self.VerifiedBlocks) < 5:
			# Verify the block, account list, and account list after transactions
			if self.VerifyBlock(block, originalAccountList, modifiedAccountList):
				for masterNode in self.MasterNodes:
					# Send block to each masternode to verify
					masterNode.VerifyBlockFromMasterNode(block, originalAccountList, modifiedAccountList)

		if len(self.VerifiedBlocks) == 5 and self.CensusInitiated == False:
			self.CensusInitiated = True
			
			# Wait for the rest of the masternodes to catch up
			fullyVerified = 0
			while fullyVerified < len(self.MasterNodes):
				fullyVerified = 0
				for masterNode in self.MasterNodes:
					if len(masterNode.VerifiedBlocks) == 5 and masterNode.CensusInitiated == True:
						fullyVerified += 1

			self.MergeVerifiedBlocks()			


			Timer(5, self.InitiateCensus).start()
			#self.InitiateCensus()


	def MergeVerifiedBlocks(self):
		'''
		In the case not all masternodes agree on blocks, this finds the most frequently agreed and sets all
		masternodes verified blocks to match
		TODO: Clean this up a bit
		'''
		
		# Number of masternodes with this block
		compiledBlocks = {}
		# Blocks themselves
		compiledBlockList = []

		# Runs through verified blocks, counting the number of times a block shows up
		for masterNode in self.MasterNodes:
			for verifiedBlock in masterNode.VerifiedBlocks:
				try:
					compiledBlocks[verifiedBlock.BlockID] += 1
				except:
					compiledBlocks[verifiedBlock.BlockID] = 0

				# Grabs the verified block if it hasn't already shown up
				if verifiedBlock.BlockID not in compiledBlocks:
					compiledBlockList.append(verifiedBlock)
		
		# Finds the most frequently occuring blocks out of the verified blocks
		maxFive = []
		while len(maxFive) < 5:
			maxItem = 0
			maxBlock = None 
			for blockID in compiledBlocks:
				if maxItem < compiledBlocks[blockID] and blockID not in maxFive:
					maxItem = compiledBlocks[blockID]
					maxBlock = blockID
			maxFive.append(maxBlock)

		# Compiles top five blocks
		VerifiedBlocks = []
		for block in compiledBlockList:
			if block.BlockID in maxFive and block not in VerifiedBlocks:
				VerifiedBlocks.append(block)

		# Assigns each masternode these 5 blocks
		for masterNode in self.MasterNodes:
			masterNode.VerifiedBlocks = VerifiedBlocks

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
		if block not in self.SelfVerifiedBlocks:
			if self.VerifyBlock(block, originalAccountList, modifiedAccountList):
				self.SelfVerifiedBlocks.append(block)
				self.VerifiedBlockCount[block.BlockID] = 0
				return True
			return False
		else:
			self.VerifiedBlockCount[block.BlockID] += 1
			if self.VerifiedBlockCount[block.BlockID] >= self.Quorum() and len(self.VerifiedBlocks) < 5:
				self.AddToVerifiedBlockList(block)
			return True


	def InitiateCensus(self):
		'''
		Once all masternodes agree on the verified blocks, census gets initiated
		This masternode will complete the census, and then will have all other masternodes complete the census
		After all masternodes have completed the census, compares against eachother
		'''
		print('Census Initiated by: ' + str(self.userID))
		self.PerformCensus()
		for masterNode in self.MasterNodes:
			masterNode.PerformCensus()
		for masterNode in self.MasterNodes:
			masterNode.CompareCensus(self.userID, self.Census)

		while not self.CensusVerified:
			continue


		self.InitiateFinalAccountListMerge()

	def InitiateFinalAccountListMerge(self):
		mergeReady = 0
		while mergeReady != len(self.MasterNodes):
			mergeReady = 0
			for masterNode in self.MasterNodes:
				if masterNode.CensusComplete == True:
					mergeReady += 1
		self.MergeCensusIntoAccountList()

		mergeReady = 0
		while mergeReady != len(self.MasterNodes):
			mergeReady = 0
			for masterNode in self.MasterNodes:
				if masterNode.CensusMergeComplete == True:
					mergeReady += 1
		self.FinalizeAccountList()


	def CompareCensus(self, masterNodeID, census):
		'''
		Compares this masternodes census against another masternodes census.
		Input:
			masterNodeID: ID of masternode the census was received from
			census: Census from masternode to compare against own
		'''
		valid = True
		# Validates that the census values are valid
		for userid in census:
			if census[userid]['Balance'] != self.Census[userid]['Balance']:
				print("Invalid census received from Masternode: " + str(masterNodeID))
				valid = False
				break
		if valid == True:
			self.VerifiedCensus.append(masterNodeID)

		if len(self.VerifiedCensus) > self.Quorum():
			#print('Census validated by:' + str(self.userID))
			self.CensusVerified = True


	def PerformCensus(self):
		'''
		Performs the census if it hasn't already been completed by going through the verified blocks
		and adding up all additions and subtractions from receivers and senders respectively
		'''
		if not self.CensusComplete:
			self.Census = self.OriginalMasterAccountList.EmptyAccountList()
			for block in self.VerifiedBlocks:
				for microblock in block.MicroBlocks:
					for transaction in microblock.TransactionList:
						self.Census[transaction.senderID]['Balance'] -= transaction.coins
						self.Census[transaction.receiverID]['Balance'] += transaction.coins
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
					print("Invalid Transaction detected by MasterNode: " + str(self.userID) + " in block sent node: " + str(block.BlockID))
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
		for userid in self.Census:
			self.ModifiedMasterAccountList.AccountList[userid]['Balance'] += self.Census[userid]['Balance']
		print('MasterNode: ' + str(self.userID) + ' has merged the census')
		self.CensusMergeComplete = True

	def FinalizeAccountList(self):
		for masterNode in self.MasterNodes:
			for userid in masterNode.ModifiedMasterAccountList.AccountList:
				if masterNode.ModifiedMasterAccountList.AccountList[userid] != self.ModifiedMasterAccountList.AccountList[userid]:
					print('Masternode ' + str(self.userID) + 'has detected a flaw in the account list of Masternode ' + str(masterNode.userID))
		print('Account List Verified for Masternode ' + str(self.userID))
		Timer(10, self.MasternodeSelection())
		#self.MasternodeSelection()
	# Census applied to account list
	# Quorum proceedure for accountlist ot define master accountlist

