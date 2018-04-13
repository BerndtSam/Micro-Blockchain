from time import sleep
import random
from threading import Timer

class Block:
    def __init__(self, userID):
        self.BlockID = userID
        self.TransactionList=[]
        self.Solved = False;
        self.Timer = Timer(random.randint(8,15), self.BlockSolved)
        
        self.Timer.start()

    def AddTransaction(self,transaction):
        if transaction not in self.TransactionList:
            self.TransactionList.append(transaction)
            return True
        else:
            return False

    def RemoveTransaction(self,transaction):
        if transaction not in self.TransactionList:
            self.TransactionList.remove(transaction)
        else:
            return True

    def BlockSolved(self):
        self.Solved = True;
        print("Block solved by: " + str(self.BlockID))

    def IsSolved(self):
        return self.Solved;

      