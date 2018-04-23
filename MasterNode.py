from Node import Node
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

	# Once recieves 5 verified blocks
	# Does Census
	# Census: zeroed out account list
	# Verifies the outcome values of 5 blocks
	# Send to each masternode
	# Follow quorum proceedure

	# Census applied to account list
	# Quorum proceedure for accountlist ot define master accountlist

