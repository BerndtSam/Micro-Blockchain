from MicroBlock import MicroBlock

class Block:
    def __init__(self, userID, microBlocksPerBlock, maxTimePerMicroBlock):
        self.BlockID = userID
        self.Solved = False;
        self.MicroBlocks = []
        self.MicroBlocksPerBlock = microBlocksPerBlock
        self.MaxTimePerMicroBlock = maxTimePerMicroBlock

        self.AddMicroBlock()

    def AddTransaction(self,transaction):
        '''
        Takes transaction from node and tells the current microblock to process it
        Input:
            transaction: Current transaction object to process
        Output:
            True: If transaction did not already exist in list, gets rid of double spending
            False: If transaction already exists in list, gets rid of double spending
        '''
        currentMicroBlock = self.MicroBlocks[-1]
        return currentMicroBlock.AddTransaction(transaction)

    def RemoveTransaction(self,transaction):
        '''
        Takes transaction from node and tells the current microblock to process it
        Input:
            transaction: Current transaction object to remove
        Output:
            True: If transaction exists in list, removes it
            False: If transaction doesn't exist in list
        '''
        currentMicroBlock = self.MicroBlocks[-1]
        return currentMicroBlock.RemoveTransaction(transaction)

    def CheckMicroBlockStatus(self):
        '''
        Used to add new microblocks if the previous one is solved, or, if all microblocks solved, solves current block
        '''
        currentMicroBlock = self.MicroBlocks[-1]
        if len(self.MicroBlocks) == self.MicroBlocksPerBlock and currentMicroBlock.IsSolved() == True:
            self.BlockSolved()
            return True
        elif currentMicroBlock.IsSolved() == True and len(self.MicroBlocks) < self.MicroBlocksPerBlock:
            self.AddMicroBlock()
            return True
        return False

    def AddMicroBlock(self):
        '''
        Initializes a new microblock with the current blocks ID, the microblock ID set to the number of microblocks, and
        sets the time it takes per microblock
        '''
        self.MicroBlocks.append(MicroBlock(self.BlockID, len(self.MicroBlocks), self.MaxTimePerMicroBlock))

    def BlockSolved(self):
        '''
        Sets the block to solved
        '''
        self.Solved = True;
        print("Block solved by: " + str(self.BlockID))

    def IsSolved(self):
        '''
        Returns if the current block is solved
        Output:
            True: If the current block is solved
            False: If the current block is not solved
        '''
        return self.Solved;

      