from AccountList import AccountList
from TransactionPool import TransactionPool


# Create initial account list
masterAccountList = AccountList()
masterAccountList.PopulateAccountList(10, rand=True)
print(masterAccountList.AccountList)

# Initialize TransactionPool
transactionPool = TransactionPool(masterAccountList)

# Generate 100 valid transactions
transactionPool.GenerateValidTransactions(100)

# Generate 1% invalid transactions
transactionPool.GeneratePercentInvalidTransactions(.01)

# Processes transactions
for transaction in transactionPool.Transactions:
	print(masterAccountList.ProcessTransaction(transaction.senderID, transaction.receiverID, transaction.coins))


#main.py
