# Micro-Blockchain
Developed by Sam Berndt

# Initialization Proceedure
1) Clone from GitHub: git clone https://github.com/BerndtSam/Micro-Blockchain.git
2) Ensure Python 3.4 or later is installed
	2.1) If it is not, visit Python's website for installation instructions
	2.1.1) https://www.python.org/
3) Ensure the statistics toolkit is installed
	3.1) pip install statistics

# Execute Program
To execute the program, run the following command on the command line using Python 3.4 or later

python main.py

If you have multiple Python versions installed, you may need to try:

python3 main.py

To reproduce the results, simply modify the variables mentioned in the Variables portion of the readme to as they are described on the paper. Take the data from the last 5 printed lines in the program and input it into the graph. We used plot.ly for charting.

Note: Due to our use of random, it is possible that not enough nodes will be eligible to be a masternode. In which case, you will notice a flood of failures to choose a masternode. End the program and restart using the above commands.


# Variables
In the main.py file, you can configure the settings of the blockchain iterations.

The defaults are as follows:
NumberOfAccounts = 100

MicroBlocksPerBlock = 5

MaxTimePerMicroBlock = 3

BlockIterations = 5

DistanceThreshold = 4

NumberOfTransactionsPerIteration = 50

You are able to adjust each of these for your own application. 

NumberOfAccounts: The total number of nodes that are active in the blockchain

MicroBlocksPerBlock: The number of microblocks that will be created per block. Microblocks that are a part of the micro blockchain. 3 and 5 work really well, 5 works most of the time

MaxTimePerMicroBlock: As the blocks are not actually solving the SHA-256 problem as proposed in the paper, you can adjust the amount of time each microblock can be solved in.

BlockIterations: The number of times you want the whole process to loop

DistanceThreshold: The theoretical distance that transactions can travel per block. Assists in proving census concept

NumberOfTransactionsPerIteration: The total number of additional transactions you want per iteration. Assists in proving census concept.

As a word of caution, increasing the number of MicroBlocksPerBlock will result in an exponential increase in threads.