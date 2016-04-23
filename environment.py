# coding: utf-8

from runFast import RunFast, Player
from scipy import zeros
import time

class RunFastEnvironment(RunFast):
	'''
	继承自RunFast类，主要是存储了一些游戏的状态信息
	这里我们先训练一个agent
	'''

	def __init__(self):
		RunFast.__init__(self)

	def doReadyWork(self, agents):
		'''
		做一些准备工作，如果环境中没有agents，则传入agents
		洗牌，发牌，设定好谁先走等
		'''
		if not self.players:
			self.addPlayer(agents)
		self.shuffle()
		self.dealCards()
		self.currentTurn = self.chooseWhoStart()

	def isOver(self):
		return self.gameOver()

	def resetEnv(self):
		self.reset()

	def getState(self):
		'''
		获得当前的状态，供网络学习
		currentPlayerCards 当前的手牌
		playedCards 已经打出的牌
		preCards 上家打出的牌
		preType 上家打出的类型
		'''
		state = {'preCards': [], 'preType': [], 'isFirst': False}
		currentPlayer = self.players[self.currentTurn]
		state['playerCards'] = currentPlayer.getCurrentCards()[:]
		state['playedCards'] = self.havePlayed[:]
		if self.currentTurn != self.whoPlayed:
			state['preCards'] = self.currentCard[:]
			state['preType'] = self.currentType[:]
		if self.whoPlayed == -1:
			state['isFirst'] = True

		return state

	def doAction(self, action):
		'''
		根据agent传来的action来进行实际行动
		并且返回新的状态和reward给agent
		如果游戏结束了，就只是改变一下玩家的turn
		'''
		ct = self.currentTurn
		playedCards = action['cards']
		playedType = action['type']
		if playedCards:
			# 如果是实际出牌的话
			# print self.players[ct].name, 'has', self.players[ct].getCurrentCards()
			# print self.players[ct].name, 'played', playedCards
			self.players[ct].removeCards(playedCards)
			self.moveToNext(playedCards, playedType)
		else:
			self.passToNext()
			# print self.players[ct].name, 'has', self.players[ct].getCurrentCards()
			# print self.players[ct].name, 'choose PASS'

		# reward = self.getReward()
		# state = self.getState()
		# return reward


