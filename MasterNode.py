class MasterNode(Node):
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
