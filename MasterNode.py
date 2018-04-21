from Node import Node
import random
import copy

class MasterNode(Node):
	def __init__(self, userID, accountList, blocksSolved, transactionPool, previousMasterNodeList):
		super(MasterNode, self).__init__(userID, accountList, blocksSolved, transactionPool)
		super(MasterNode, self).SetMasterNode(True)
		self.PreviousMasterNodeList = previousMasterNodeList
		self.ReplacementMasterNode = None
		self.SelectedMasterNodes = []
		self.CurrentMasterNodeIDs = []

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
		AvailableMasterNodes = [Node for Node in self.OriginalAccountList.AccountList if self.OriginalAccountList.AccountList[Node]['NumberOfBlocksSolved'] >= self.OriginalAccountList.MedianBlocksSolved() and Node not in self.PreviousMasterNodeList and Node not in self.CurrentMasterNodeIDs]
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
				self.OriginalAccountList = copy.deepcopy(self.ModifiedAccountList)
				self.ModifiedAccountList = copy.deepcopy(self.ModifiedAccountList)

				print("MasterNodeID: " + str(self.userID) + " initialized as a new MasterNode")
				break






	# Selection
	# Selection happens after end of block iteration
	# User must have greater or equal to the median number of blocks solved to be masternode
	# Receives accountlist, new masternode list
	# Sends announce to each node saying its the new masternode
	# Send account list to each masternode and does quorum to verify
	# If masternode deos not have same accountlist, gets dropped
	# Must ping every 15 seconds
	# must respond to pings

	# Block processing
	# does not mine this or next block
	# Takes in Blocks from Nodes
	# Verifies content of blocks and matching of original and modified account list
	# Flags the block as verified
	# Sends to other masternodes
	# Once receives 1 from other quorum of masternodes
	# Adds to verified block list
	# Once recieves 5 verified blocks
	
	# Does Census
	# Census: zeroed out account list
	# Verifies the outcome values of 5 blocks
	# Send to each masternode
	# Follow quorum proceedure

	# Census applied to account list
	# Quorum proceedure for accountlist ot define master accountlist

	# choose new masternodes
	# send everything accountlist
	# Send masternode list
	# send current masternode list
