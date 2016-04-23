# coding: utf-8
__author__ = 'zhangyidong'

from runFast import Player, RunFast
import os, sys
from collections import Counter
import time
import random

NNINPUT = ['14A','15A','3A','4A','5A','6A','7A','8A','9A','10A','11A','12A','13A',
        '14B','3B','4B','5B','6B','7B','8B','9B','10B','11B','12B','13B',
        '14C','3C','4C','5C','6C','7C','8C','9C','10C','11C','12C','13C',
        '3D','4D','5D','6D','7D','8D','9D','10D','11D','12D','13D',
        '14A','15A','3A','4A','5A','6A','7A','8A','9A','10A','11A','12A','13A',
        '14B','3B','4B','5B','6B','7B','8B','9B','10B','11B','12B','13B',
        '14C','3C','4C','5C','6C','7C','8C','9C','10C','11C','12C','13C',
        '3D','4D','5D','6D','7D','8D','9D','10D','11D','12D','13D',
        '14A','15A','3A','4A','5A','6A','7A','8A','9A','10A','11A','12A','13A',
        '14B','3B','4B','5B','6B','7B','8B','9B','10B','11B','12B','13B',
        '14C','3C','4C','5C','6C','7C','8C','9C','10C','11C','12C','13C',
        '3D','4D','5D','6D','7D','8D','9D','10D','11D','12D','13D',
        '14A','15A','3A','4A','5A','6A','7A','8A','9A','10A','11A','12A','13A',
        '14B','3B','4B','5B','6B','7B','8B','9B','10B','11B','12B','13B',
        '14C','3C','4C','5C','6C','7C','8C','9C','10C','11C','12C','13C',
        '3D','4D','5D','6D','7D','8D','9D','10D','11D','12D','13D',]

class RunFastAgent(Player):
    '''
    继承自Player类，用来执行出牌的操作
    controller用来存储Q值，这里实际上是一个神经网络
    通过和环境交互来进行学习，训练出一个收敛的神经网络
    函数都是通过experiment进行调用
    '''

    def __init__(self, name, controller, alpha=0.5, gamma=0.9):
        '''
        存储laststate，以便在新的state到来的时候更新controller
        '''
        Player.__init__(self, name)
        self.controller = controller
        self.laststate = None 
        self.lastaction = None
        self.lastreward = None
        self.alpha = alpha
        self.gamma = gamma

    def setTurn(self, turn):
        self.controller.turn = turn

    def reset(self):
        self.laststate = None 
        self.lastaction = None
        self.lastreward = None

    def getAction(self, state, epsilon=0.1, type=1):
        '''
        根据当前的牌面状态选择一个action, 这里根据epsilon-greedy来进行选择
        return dict{cards，type}
        '''
        ranNum = random.random()
        if ranNum <= epsilon:
            # print 'pick a action from random'
            preCards = state['preCards']
            preType = state['preType']
            if state['isFirst']:
                return self.playCardsWithHart3()
            if preCards:
                return self.playRandomByPreCards(preType, preCards)
            else:
                return self.playRandom()
        else:
            return self.getBestAction(state, type=type)

    def getActions(self, state):
        '''
        找出当前状态下所有可能的打法
        '''
        preCards = state['preCards']
        preType = state['preType']
        isFirst = state['isFirst']
        playerCards = state['playerCards']
        # cardsCanPlay = self.getCardsCanPlay(preType, preCards, isFirst)
        tempPlayer = Player('temp')
        tempPlayer.cards = playerCards
        cardsCanPlay = tempPlayer.getCardsCanPlay(preType, preCards, isFirst)
        return cardsCanPlay

    def getBestAction(self, state, type=1):
        '''
        这里有几种方法来实现，先说最简单的。
        直接对当前的状态s取各个可能的action的Q值，max的那个a就可以作为best
        '''
        actionDict = self.getActions(state)
        # time.sleep(1)
        # print actionDict
        bestAction = []
        bestType = None
        bestValue = None
        for naType in actionDict.keys():
            # print naType
            for a in actionDict[naType]:
                action = [self.cards[i] for i in a]
                inp = self.getInput(state, action, type=type)
                value = self.controller.getValue(inp)
                if not bestValue:
                    bestValue = value
                    bestType = naType
                    bestAction = action
                if  value > bestValue:
                    bestValue = value
                    bestType = naType
                    bestAction = action
        return {'cards': bestAction, 'type': bestType}

    @ classmethod
    def getInput(self, state, action, type=1):
        '''
        获得当前的状态，供网络学习
        playerCards 当前的手牌
        playedCards 已经打出的牌
        preCards 上家打出的牌
        actions 这一轮的走牌
        在获取input时，我们可以创建多种features，不同的features的效果自然不同，这里将所有的input写在一起，便于管理
        '''
        playerCards = state['playerCards']
        playedCards = state['playedCards']
        preCards = state['preCards']
        if type == 1:
            input = [0] * 192
            for i, c in enumerate(NNINPUT):
                if i < 48 and c in playerCards:
                    input[i] = 1
                elif 48 <= i < 96 and c in playedCards:
                   input[i] = 1
                elif 96 <= i < 144 and c in preCards:
                    input[i] = 1   
                elif 144 <= i < 192  and c in action:
                    input[i] = 1
            return input
        elif type == 2:
            input = [0] * 52
            print state, action
            offset = -3
            for card in playerCards:
                c_n = int(card[0:-1])
                input[c_n+offset] += 1
            offset += 13
            for card in playedCards:
                c_n = int(card[0:-1])
                input[c_n+offset] += 1
            offset += 13
            for card in preCards:
                c_n = int(card[0:-1])
                input[c_n+offset] += 1
            offset += 13
            for card in action:
                c_n = int(card[0:-1])
                input[c_n+offset] += 1
            return input

    def learn(self, state, lastreward, lastState = None, lastAction = None, type=1):
        '''
        算出target Qvalue，传给控制器进行学习
        qvalue_n+1 = (1-alpha) * qvalue + alpha*(r + gamma * max(qvalue_next))
        怎么处理最后一次优化：最后一次时，我们获得了终盘的状态和回报，这时候，应该没有max（）的这一项了，因为没有action可走了，所有去掉这一项
        '''
        if not lastState and not lastAction:
            lastState = self.laststate
            lastAction = self.lastaction

        if self.lastaction == None and self.laststate == None:
            return False
        # print self.laststate
        input = self.getInput(lastState, lastAction, type=type)
        qValue = self.controller.getValue(input)
        qNextValues = []
        if state:
            nextActionsDict = self.getActions(state)
            for naType in nextActionsDict.keys():
                for a in nextActionsDict[naType]:
                    action = [state['playerCards'][i] for i in a]
                    inp = self.getInput(state, action, type=type)
                    qNextValues.append(self.controller.getValue(inp))
        maxQ = 0
        if qNextValues:
            maxQ = max(qNextValues)

        targetValue = (1 - self.alpha) * qValue + self.alpha * (lastreward + self.gamma * maxQ)
        # print self.name, '(1 - ',self.alpha,') * ',qValue,' + ',self.alpha,' * (',lastreward,' + ',self.gamma,' * ',maxQ, ')'
        self.controller.train(input, targetValue)

    def saveNet(self):
        if not os.path.isdir(self.controller.name):
            os.mkdir(self.controller.name)
        self.controller.saveNet()

class RunFastAgentWithMemory(RunFastAgent):
    '''
    这个agent存储了replay memory，用来做更新
    这样就可以防止进入局部最优
    '''

    def __init__(self, name, controller):
        RunFastAgent.__init__(self, name, controller)
        self.memories = []

    def saveMemory(self, lastreward, state, action=None, capacity=10000):
        '''
        用于存储之前的行动状态，用于之后的更新
        memory [laststate, lastaction, lastreward, nextState]
        只存储一定的量，超过这个量，就把之前的记录给删除
        '''
        if len(self.memories) >= capacity:
            self.memories.pop(0)
        if not self.lastaction:
            self.lastaction = action
            self.laststate = state
        else:
            memory = (self.laststate, self.lastaction, lastreward, state)
            self.memories.append(memory)
            self.lastaction = action
            self.laststate = state


    def learnFromMemory(self, learn_num=10, type=1):
        '''
        从memory中调出数据进行学习，随机的取出历史数据进行学习，防止陷入局部最优
        '''
        memories_len = len(self.memories)
        if memories_len < learn_num:
            learn_num = memories_len
        for i in xrange(learn_num):
            memory = random.choice(self.memories)
            self.learn(memory[3], memory[2], lastState=memory[0], lastAction=memory[1], type=type)


