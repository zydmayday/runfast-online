# coding: utf-8
from pybrain.tools.shortcuts import buildNetwork
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.datasets import SupervisedDataSet
import pickle
import os
import time
from agent import RunFastAgent

class RunFastNetwork():
	'''
	用来存储runfast游戏中agent的Q值
	'''
	def __init__(self, name='', inputNum=192, hiddenNum=192, outNum=1):
		self.net = buildNetwork(inputNum, hiddenNum, outNum)
		self.ds = SupervisedDataSet(inputNum, outNum)
		self.name = name
		self.turn = 0

	def train(self, input, output):
		self.ds.clear()
		self.ds.addSample(input, output)
		trainer = BackpropTrainer(self.net, self.ds)
		trainer.train()

	def addLearner(self, learner):
		self.learner = learner

	def saveNet(self, filename=''):
		with open(self.name  + '/' + str(self.turn), 'w') as f:
			print self.name  + '/' + str(self.turn), ' has saved'
			pickle.dump(self, f)

	def loadNet(self, playName, turn=0):
		if os.path.isfile(playName  + '/' + str(turn)):
			with open(self.name  + '/' + str(turn), 'r') as f:
				print 'loading ', playName  + '/' + str(turn)
				time.sleep(0.5)
				obj = pickle.load(f)
				print obj.turn
				self.turn = obj.turn
				self.net = obj.net
				self.name = obj.name

	def getValue(self, input):
		return self.net.activate(input)

class RunFastDeepNetwork(RunFastNetwork):

	def __init__(self, name='', inputNum=192, hidden1Num=192, hidden2Num=192, hidden3Num=192, outNum=1):
		RunFastNetwork.__init__(self, name)
		self.net = buildNetwork(inputNum, hidden1Num, hidden2Num, hidden3Num, outNum)

class StateNetwork():
	'''
	用来存储状态转移的函数的，具体来说就是我给定一个input，返回给我下一个时刻的状态
	下一个时刻的状态不包括action
	'''
	def __init__(self, name='deep_state', inputNum=192, hidden1Num=192, hidden2Num=192, hidden3Num=192, outNum=144):
		self.net = buildNetwork(inputNum, hidden1Num, hidden2Num, hidden3Num, outNum)
		self.ds = SupervisedDataSet(inputNum, outNum)
		self.name = name
		self.turn = 0

	def train(self, input, output):
		self.ds.clear()
		self.ds.addSample(input, output)
		trainer = BackpropTrainer(self.net, self.ds)
		trainer.train()


	def saveNet(self):
		if not os.path.isdir(self.name):
			os.mkdir(self.name)
		print self.name  + '/' + str(self.turn), ' has saved'
		with open(self.name  + '/' + str(self.turn), 'w') as f:
			pickle.dump(self.net, f)

	def loadNet(self, turn=0):
		print 'loading ', self.name  + '/' + str(turn)
		time.sleep(1)
		if os.path.isfile(self.name  + '/' + str(turn)):
			with open(self.name  + '/' + str(turn), 'r') as f:
				self.net = pickle.load(f)

	def getValue(self, input):
		output = self.net.activate(input)
		for i,v in enumerate(output):
			if v > 0.5:
				output[i] = 1
			else:
				output[i] = 0
		return output

	def getInput(self, state, action, type=1):
		return RunFastAgent.getInput(state, action, type=type)

	def getOutput(self, state):
		input = RunFastAgent.getInput(state, [])
		return input[:144]

if __name__ == '__main__':
	pass
	# rfn = RunFastNetwork()
	# rfn.train([1,2,3], 2)
	# print rfn.getValue([1,2,3,])
	# rfn.saveNet('net1')
	# f = open('net1', 'r')
	# net = pickle.load(f)
	# print net.getValue([1,2,3])
	# sn = StateNetwork()
	# input = [i for i in range(0,192)]
	# print sn.getValue(input)
