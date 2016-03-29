# coding:utf-8
__author__ = 'zhangyidong'

from random import random, choice
import re
from collections import Counter
import time

# 红桃A，方块B，草花C，黑桃D
CARDCASE = ['14A','15A','3A','4A','5A','6A','7A','8A','9A','10A','11A','12A','13A',
        '14B','3B','4B','5B','6B','7B','8B','9B','10B','11B','12B','13B',
        '14C','3C','4C','5C','6C','7C','8C','9C','10C','11C','12C','13C',
        '3D','4D','5D','6D','7D','8D','9D','10D','11D','12D','13D',]

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

HART3 = '3A'

TYPES = ['SINGLE', 'PAIR', 'THREE', 'CONTIPAIR', 'CONTITHREE', 'BOMB', 'THREETWO', 'PLANE', 'FLUSH']

PASS = []
PASSTYPE = 'PASS'

class RunFast():

    def __init__(self, players=None):
        self.player_num = 3
        self.players = []
        if players:
            self.players = players
        self.cards = CARDCASE[:]
        self.currentTurn = 0
        self.currentCard = [] # 当前场上打出的牌
        self.currentType = []
        self.whoPlayed = -1
        self.havePlayed = []
            
    def shuffle(self):
        '''
        将一副新牌洗开
        '''
        tempCards = []
        cards = self.cards
        while len(cards) > 0:
            chosedCard = choice(cards)
            cards.remove(chosedCard)
            tempCards.append(chosedCard)
        self.cards = tempCards

    def dealCards(self):
        '''
        发牌
        '''
        for i in range(0, 48, 3):
            self.players[0].recieveOneCard(self.cards[i])
            self.players[1].recieveOneCard(self.cards[i+1])
            self.players[2].recieveOneCard(self.cards[i+2])

    def chooseWhoStart(self):
        '''
        有红桃三的先走
        '''
        player = None
        for p in self.players:
            if HART3 in p.getCurrentCards():
                player = p
        return self.players.index(player)

    def moveToNext(self, playedCards, playedType):
        self.whoPlayed = self.currentTurn
        self.currentCard = playedCards
        self.currentType = playedType
        self.havePlayed += playedCards
        if self.currentTurn > 1:
            self.currentTurn = 0
        else:
            self.currentTurn += 1

    def passToNext(self):
        if self.currentTurn == self.whoPlayed or self.whoPlayed == -1:
            return False
        if self.currentTurn > 1:
            self.currentTurn = 0
        else:
            self.currentTurn += 1
        return True

    def getReward(self, player):
        if not self.gameOver():
            return 0
        else:
            cc = player.getCurrentCards()
            if cc:
                return -len(cc)
            else:
                r = 0
                for p in self.players:
                    if p not in self.players:
                        r += len(p.getCurrentCards())
                return r

    def getPlayers(self):
        return self.players

    def getPlayer(self, name):
        for p in self.players:
            if p.name == name:
                return p

    def addPlayer(self, players):
        self.players = players

    def start(self):
        '''
        开始游戏
        '''
        print 'GAME START!'
        time.sleep(0.5)
        for p in players:
            p.sortCards()
            print p.name, ' has cards: ', p.getCurrentCards()
        self.currentTurn = self.chooseWhoStart()
        self.currentCard, self.currentType = self.players[self.currentTurn].playFirstCards()
        self.havePlayed += self.currentCard
        print '-------------------------'
        print self.players[self.currentTurn].name, 'played', self.currentCard
        self.whoPlayed = self.currentTurn
        while not self.gameOver():
            if self.currentTurn > 1:
                self.currentTurn = 0
            else:
                self.currentTurn += 1
            # 如果转一圈回来没有人出牌，则这个人接着出别的牌
            if self.currentTurn == self.whoPlayed:
                print '-------------------------'
                self.currentCard, self.currentType = self.players[self.currentTurn].playCards()
                self.havePlayed += self.currentCard
                print self.players[self.currentTurn].name, 'played', self.currentCard
            else:
                playedCard, type = self.players[self.currentTurn].playCards(preCards = self.currentCard, preCardsType=self.currentType)
                if playedCard == PASS:
                    print self.players[self.currentTurn].name, 'choose PASS'
                else:
                    self.currentCard = playedCard
                    self.whoPlayed = self.currentTurn
                    self.havePlayed += self.currentCard
                    print self.players[self.currentTurn].name, 'played', self.currentCard

        print 'GAME IS OVER!'
        for p in players:
            name = p.name
            cards = p.getCurrentCards()
            if not cards:
                print name, 'WIN!'
            else:
                print name, ' still has ', cards



    def gameOver(self):
        '''
        判断游戏是否结束
        '''
        for p in self.players:
            if len(p.getCurrentCards()) == 0:
                return True

    def reset(self):
        self.cards = CARDCASE[:]
        self.currentTurn = 0
        self.currentCard = [] 
        self.currentType = []
        self.whoPlayed = -1
        for p in self.players:
            p.clearCards()

    def getSensor(self):
        '''
        获得当前的状态，供网络学习
        currentPlayerCards 当前的手牌
        playedCards 已经打出的牌
        preCards 上家打出的牌
        '''
        obs = zeros(144)
        currentPlayer = self.players[self.currentTurn]
        currentPlayerCards = currentPlayer.getCurrentCards()
        playedCards = self.havePlayed
        preCards = self.currentCard

        for i, c in enumerate(NNINPUT):
            if i < 48 and c in currentPlayerCards:
                obs[i] = 1
            elif 48 <= i < 96 and c in playedCards:
               obs[i] = 1
            elif 96 <= i < 144 and c in preCards:
                obs[i] = 1   

        return obs


class Player():

    def __init__(self, name):
        self.name = name
        self.cards = []

    def recieveOneCard(self, card):
        '''
        将发的牌收入自己手中
        '''
        self.cards.append(card)

    def recieveCards(self, cards):
        self.cards = cards

    def _natural_sort(self, l): 
        convert = lambda text: int(text) if text.isdigit() else text.lower() 
        alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
        return sorted(l, key = alphanum_key)

    def sortCards(self):
        '''
        理牌
        '''
        # self.cards = ['4B', '5C', '5D', '6A', '7B','7A','7C','7D', '8C', '10D','11B','12B','12C','13A','13B','14B',]
        self.cards = self._natural_sort(self.cards)

    def getCurrentCards(self):
        '''
        获取自己当前手牌
        '''
        return self.cards   

    def clearCards(self):
        self.cards = []

    def removeCards(self, playCards):
        for c in playCards:
            self.cards.remove(c)

    def _getContinue(self, cards, preCards=None, basicCards=None, type='pair'):
        '''
        首先获取基础牌，basicCards，表示我想要做的连接的所有牌，比如在连对中，把所有的对子都传过来。
        numContiDict：用来统计每个数字的对子。比如，key为数字，value为该数字可能的对子的数组。
        将所有的（连对/钢板/顺子）可能情况列出来，比如对于5，6，7，就有[(5,6),(6,7),(5,6,7)]
        最后，针对每一种情况，例如把数字相同的对子（花色不同）拎出来排列组合。
        '''        
        numContiDict = {}
        returncontiCards = []
        preCardsDict = {'num': 1, 'len': None}
        if preCards:
            if type == 'pair':
                preCardsDict = {'num': preCards[0], 'len': len(preCards)/2}
            elif type == 'three':
                preCardsDict = {'num': preCards[0], 'len': len(preCards)/3}
            elif type == 'flush':
                preCardsDict = {'num': preCards[0], 'len': len(preCards)}

        for bc in basicCards:
            num = cards[bc[0]]
            if not numContiDict.has_key(num):
                numContiDict[num] = [bc]
            else:
                numContiDict[num].append(bc)

        basicNums = numContiDict.keys()
        basicNums.sort()
        firstNum = 0
        possibleContiCards = []
        for i in range(0, len(basicNums) - 1):
            contiCards = [basicNums[i]]
            startNum = basicNums[i]
            for j in range(i+1, len(basicNums)):
                nextNum = basicNums[j]
                if nextNum == startNum + 1:
                    contiCards.append(nextNum)
                    if preCards:
                        if preCardsDict['num'] < contiCards[0] and preCardsDict['len'] == len(contiCards):
                            possibleContiCards.append(contiCards[:])
                    else:
                        if type == 'flush':
                            if contiCards[-1] != 15 and len(contiCards) >= 5:
                                possibleContiCards.append(contiCards[:])
                        else:
                            possibleContiCards.append(contiCards[:])
                else:
                    break
                startNum += 1

        # print 'possibleContiCards',possibleContiCards

        for pcp in possibleContiCards:
            # print 'pcp',pcp
            firstCards = []
            secondCards = []
            for num in pcp:
                if len(firstCards) == 0:
                    for pair in numContiDict[num]:
                        firstCards.append(pair)
                else:
                    secondCards = []
                    for i in range(0, len(firstCards)):
                        for pair in numContiDict[num]:
                            secondCards.append(firstCards[i] + pair)
                    firstCards = secondCards[:]
            # print secondCards
            returncontiCards += secondCards[:]
        return returncontiCards

    def getSingle(self, cards, preCards=None):
        '''
        出单张
        '''
        returnCards = []
        for i, c in enumerate(cards):
            if preCards:
                if c > preCards[0]:
                    returnCards.append([i])
            else:
                returnCards.append([i])
        return returnCards, 'SINGLE'

    def getPairs(self, cards, preCards=None):
        '''
        获取可以打出的对子
        如果打不过上家的牌，则从可出的牌里删除
        '''
        cardsLen = len(cards)
        cardsCanPlay = []
        returnCards = []
        for i in range(0, cardsLen-1):
            for j in range(i+1, cardsLen):
                if cards[i] == cards[j]:
                    if preCards:
                        if preCards[0] < cards[i]:
                            cardsCanPlay.append([i, j])
                    else:
                        cardsCanPlay.append([i, j])
        # for i in range(0, cardsLen-1):
        #     if cards[i] == cards[i+1]:
        #         if preCards:
        #             if preCards[0] < cards[i]:
        #                 cardsCanPlay.append([i, i+1])
        #         else:
        #             cardsCanPlay.append([i, i+1])
        return cardsCanPlay, 'PAIR'

    def getThree(self, cards, preCards=None):
        '''
        获得三个头的不带
        '''
        returnCards = []
        cardsLen = len(cards)
        preNum = 0
        if preCards:
            preNum = preCards[0]

        for i in range(0, cardsLen-2):
            for j in range(i+1, cardsLen-1):
                if cards[i] == cards[j]:
                    for k in range(j+1, cardsLen):
                        if cards[j] == cards[k]:
                            if preCards:
                                if cards[i] > preNum:
                                    returnCards.append([i, j, k])
                            else:
                                returnCards.append([i, j, k])

        return returnCards, 'THREE'

    def getContiPairs(self, cards, preCards=None, pairCards=None):
        '''
        获得连对,针对上家的连对，要打出相同数量的牌才行
        '''
        if not pairCards:
            pairCards, type = self.getPairs(cards)

        return self._getContinue(cards, preCards, pairCards, 'pair'), 'CONTIPAIR'

    

    def getThreeTwo(self, cards, preCards=None, pairCards=None):
        '''
        获取可以打出的三带二
        '''
        cardsLen = len(cards)
        preNum = 0
        threeCards = []
        cardsCanPlay = []
        returnCards = []

        if preCards:
            # print 'preCards', preCards
            if preCards[0] == preCards[2]:
                preNum = preCards[0]
            else:
                preNum = preCards[-1]
        if not pairCards:
            pairCards, type = self.getPairs(cards)
            # print 'pairCards',pairCards
        threeCards, type = self.getThree(cards)

        for three in threeCards:
            if preCards:
                if preNum < cards[three[0]]:
                    for pair in pairCards:
                        if pair[0] not in three and pair[1] not in three:
                            returnCards.append(three + pair)
            else:
                for pair in pairCards:
                    if pair[0] not in three and pair[1] not in three:
                        returnCards.append(three + pair)

        return returnCards, 'THREETWO'

    def getContiThree(self, cards, preCards=None, threeCards=None):
        '''
        获取钢板
        '''
        if not threeCards:
            threeCards, type = self.getThree(cards)
        
        return self._getContinue(cards, preCards, threeCards, 'three'), 'CONTITHREE'



    def getBomb(self, rawCards, preCards=None):
        '''
        出炸弹。ACE炸可以任意时候出，3炸只能在别人不是炸的时候出。
        判断上家是不是炸弹，如果是炸弹，则不能出3炸。
        '''
        returnCards = []
        cardsLen = len(rawCards)
        preNum = 0
        isBomb = False
        if preCards:
            if len(preCards) == 3 and preCards[0] == preCards[1] == preCards[2]:
                isBomb = True
            if len(preCards) == 4 and preCards[0] == preCards[1] == preCards[2] == preCards[3]:
                isBomb = True
        if preCards:
            preNum = preCards[0]
        for i in range(0, cardsLen-3):
            if rawCards[i][:-1] == rawCards[i+1][:-1] == rawCards[i+2][:-1] == rawCards[i+3][:-1]:
                if isBomb:
                    if int(rawCards[i][:-1]) > preNum:
                        returnCards.append([i, i+1, i+2, i+3])
                else:
                    returnCards.append([i, i+1, i+2, i+3])
        if '1A' in rawCards and '1B' in rawCards and '1C' in rawCards:
            returnCards.append([0,1,2])
        if not isBomb and '3D' in rawCards and '3B' in rawCards and '3C' in rawCards :
            returnCards.append([rawCards.index('3B'),rawCards.index('3C'),rawCards.index('3D')])
        return returnCards, 'BOMB'

    def getPlane(self, cards, preCards=None):
        '''
        打飞机。三个头的连只加两个单张或者是对子
        prelen means the # of three cards
        return type is index, not the number of cards
        '''
        returnCards = []
        cardsLen = len(cards)
        preCardsDict = {'num':0,'len':0, 'type':1}

        if preCards:
            '''
            here we need to condider the different situations
            if we have the cards like : 333,444,555,666, we default that the player played [444555666]+333, then preNum should be 4,
            otherwise, if we have the cards form like 333444555,777, then the preNum should be 3. There is one another situation that we should consider: 555,6666,7, or the similar form like 4444,5555,6666
            these are not gonna happen in the real games, but they are still the situations we should consider about.
            the other case we should consider:
            333,444,5,7
            333,444,55,77
            333,444,555,77,8
            333,444,555,7,8,9
            333,444,555,77,88,99
            333,444,555,7777,99
            since we have so many types of the cards form, but they all obey the rules that 3+1 has cards number(4n), and the 3+2 cards has the cards number(5n).

            I think there may still be some bugs in this algorithm, maybe I will find them in the future tests.
            '''
            countedPreCards = Counter(preCards)
            if preCards:
                preNum = 0
                preType = 1
                preCardsLen = len(preCards)
                preList = [key for key, value in countedPreCards.items() if value == 3]
                preList.sort()
                if preCardsLen % 5 == 0:
                    preLen = len(preList)
                    preNum = preList[0]
                    preType = 2
                    preLen = len(preList)
                else:
                    preList = [key for key, value in countedPreCards.items() if value >= 3]
                    preList.sort()
                    preNum = preList[0]
                    preLen = len(preList)
                    if len(preList) == 4 and preCardsLen == 12 or len(preList) == 5 and preCardsLen == 16:
                        preLen = len(preList) - 1
                        if preList[-2] == preList[-1]-1:
                            preNum = preList[1]

            preCardsDict = {'num': preNum, 'len': preLen, 'type': preType}
            # print 'preCardsDict', preCardsDict
        contiThrees, type = self.getContiThree(cards)
        # print 'contiThrees', contiThrees
        for ct in contiThrees:
            if preCards:
                if len(ct) / 3 == preCardsDict['len']:
                    # print ct
                    if cards[ct[0]] > preCardsDict['num']:
                        idx = 0
                        loopNum = preCardsDict['len']
                        # 如果是飞机带单张的话
                        if preCardsDict['type'] == 1:
                            # print 'play single'
                            singleList = []
                            while idx < loopNum:
                                if not singleList:
                                    for i in range(cardsLen-loopNum+idx+1):
                                        if i not in ct:
                                            singleList.append([i])
                                else:
                                    for list in singleList:
                                        start = list[-1]
                                        for j in range(start+1, cardsLen-loopNum+idx+1):
                                            if j not in ct:
                                                singleList.append(list[:] + [j])
                                idx += 1
                            singleList = [list for list in singleList if len(list) == loopNum]
                            # print 'singleList', singleList
                            for list in singleList:
                                returnCards.append(ct + list)
                        else:
                            pairs, type = self.getPairs(cards)
                            pairs = [pair for pair in pairs if pair[0] not in ct and pair[1] not in ct]
                            idx = 0
                            pairsList = []
                            while idx < loopNum:
                                if not pairsList:
                                    for i in pairs:
                                        pairsList.append(i)
                                else:
                                    for list in pairsList:
                                        start = pairs.index([list[-2], list[-1]])
                                        for j in range(start+1, len(pairs)-loopNum+idx+1):
                                            if pairs[j][0] not in list and pairs[j][1] not in list:
                                                pairsList.append(list[:] + pairs[j])
                                idx += 1
                            pairsList = [list for list in pairsList if len(list) == loopNum*2]
                            for list in pairsList:
                                returnCards.append(ct + list)
            else:
                idx = 0
                loopNum = len(ct) / 3
                singleList = []
                while idx < loopNum:
                    if not singleList:
                        for i in range(cardsLen-loopNum+idx+1):
                            if i not in ct:
                                singleList.append([i])
                    else:
                        for list in singleList:
                            start = list[-1]
                            for j in range(start+1, cardsLen-loopNum+idx+1):
                                if j not in ct:
                                    singleList.append(list[:] + [j])
                    idx += 1
                singleList = [list for list in singleList if len(list) == loopNum]

                for list in singleList:
                    returnCards.append(ct + list)
                pairs, type = self.getPairs(cards)
                pairs = [pair for pair in pairs if pair[0] not in ct and pair[1] not in ct]
                idx = 0
                pairsList = []
                while idx < loopNum:
                    if not pairsList:
                        for i in pairs:
                            pairsList.append(i)
                    else:
                        for list in pairsList:
                            start = pairs.index([list[-2], list[-1]])
                            for j in range(start+1, len(pairs)-loopNum+idx+1):
                                if pairs[j][0] not in list and pairs[j][1] not in list:
                                    pairsList.append(list[:] + pairs[j])
                    idx += 1
                pairsList = [list for list in pairsList if len(list) == loopNum*2]
                for list in pairsList:
                    returnCards.append(ct + list)
        return returnCards, 'PLANE'

    def getFlush(self, rawCards, preCards=None):
        '''
        顺子，最少五张，要对
        '''
        rawCardsTemp = rawCards[:]
        if preCards:
            for i, pct in enumerate(preCards):
                if pct == 14:
                    preCards[i] = 1
                elif pct == 15:
                    preCards[i] = 2
            preCards.sort()

        cards = []
        for card in self.cards:
            card = int(card[0:-1])
            cards.append(card)
        cardsIndex = [[i] for i in range(0, len(cards))]
        flushWoTwo = self._getContinue(cards, preCards, cardsIndex, 'flush')

        # print 'rawCards',rawCards
        for idx, c in enumerate(rawCards):
            if c.startswith('14'):
                rawCards[idx] = '1' + c[-1:]
            elif c.startswith('15'):
                rawCards[idx] = '2' + c[-1:]

        # print 'rawCards',rawCards

        rawCards = [i for i in rawCards if int(i[:-1]) <=6]
        rawCards.sort()
        # print 'rawCards',rawCards
        cards = [int(i[:-1]) for i in rawCards]
        cardsIndex = [[i] for i in range(0, len(cards))]
        flushWithTwo = self._getContinue(cards, preCards, cardsIndex, 'flush')
        for i,flush in enumerate(flushWithTwo):
            for j,c in enumerate(flush):
                if rawCards[c].startswith('1'):
                    flushWithTwo[i][j] = '14' + rawCards[c][-1:]
                elif rawCards[c].startswith('2'):
                    flushWithTwo[i][j] = '15' + rawCards[c][-1:]
                else:
                    flushWithTwo[i][j] =  rawCards[c]
        for flush in flushWithTwo:
            flushWoTwo.append([rawCardsTemp.index(i) for i in flush])
        # print 'flushWithTwo',flushWithTwo
        # print 'flushWoTwo', flushWoTwo
        return flushWoTwo, 'FLUSH'

    def getCardType(self, preCards):
        preCardsLen = len(preCards)
        countedPreCards = Counter(preCards)
        preCardsKey = countedPreCards.keys()
        if preCardsLen == 1:
            return 'SINGLE'
        elif preCardsLen == 2:
            return 'PAIR'
        elif preCardsLen == 3:
            if '1A' in preCards and '1B' in preCards and '1C' in preCards:
                return 'BOMB'
            if '3D' in preCards and '3B' in preCards and '3C' in preCards :
                return 'BOMB'
            return 'THREE'
        elif preCardsLen == 4:
            if len(preCardsKey) == 1:
                return 'BOMB'
            else:
                return 'CONTIPAIR'
        elif preCardsLen == 5:
            if len(preCardsKey) == 2:
                return 'THREETWO'
            else:
                return 'FLUSH'

    def getCardsCanPlay(self, preType=None, preCards=None, isFirst=False):
        playIndexes = []
        playType = ''
        currentCards = [int(card[0:-1]) for card in self.cards]
        preCardsTemp = []
        # print preCards
        if preCards:
            preCardsTemp = [int(card[0:-1]) for card in preCards]
        preCardsTemp.sort()
        playIndexesDict = {}

        hartThree = 0
        if isFirst:
            hartThree = self.cards.index(HART3)

        if preCards:
            if preType == 'SINGLE':
                playIndexes,playType = self.getSingle(currentCards, preCardsTemp)
            elif preType == 'PAIR':
                playIndexes,playType = self.getPairs(currentCards, preCardsTemp)
            elif preType == 'THREE':
                playIndexes,playType = self.getThree(currentCards, preCardsTemp)
            elif preType == 'CONTIPAIR':
                playIndexes,playType = self.getContiPairs(currentCards, preCardsTemp)
            elif preType == 'THREETWO':
                playIndexes,playType = self.getThreeTwo(currentCards, preCardsTemp)
            elif preType == 'FLUSH':
                playIndexes,playType = self.getFlush(self.cards[:], preCardsTemp)
            elif preType == 'CONTITHREE':
                playIndexes,playType = self.getContiThree(currentCards, preCardsTemp)
            elif preType == 'PLANE':
                playIndexes,playType = self.getPlane(currentCards, preCardsTemp)

            # elif preType == 'BOMB':
            bomb,type = self.getBomb(self.cards[:], preCardsTemp)
            playIndexesDict[playType] = playIndexes
            playIndexesDict[type] = bomb

            playIndexesDict[PASSTYPE] = [PASS]
        else:
            playIndexes,playType = self.getSingle(currentCards)
            if playIndexes:
                if isFirst:
                    playIndexes = [i for i in playIndexes if hartThree in i]
                playIndexesDict[playType] = playIndexes[:]
            playIndexes,playType = self.getPairs(currentCards)
            if playIndexes:
                if isFirst:
                    playIndexes = [i for i in playIndexes if hartThree in i]
                playIndexesDict[playType] = playIndexes[:]
            playIndexes,playType = self.getThree(currentCards)
            if playIndexes:
                if isFirst:
                    playIndexes = [i for i in playIndexes if hartThree in i]
                playIndexesDict[playType] = playIndexes[:]
            playIndexes,playType = self.getBomb(self.cards[:])
            if playIndexes:
                if isFirst:
                    playIndexes = [i for i in playIndexes if hartThree in i]
                playIndexesDict[playType] = playIndexes[:]
            playIndexes,playType = self.getContiPairs(currentCards)
            if playIndexes:
                if isFirst:
                    playIndexes = [i for i in playIndexes if hartThree in i]
                playIndexesDict[playType] = playIndexes[:]
            playIndexes,playType = self.getThreeTwo(currentCards)
            if playIndexes:
                if isFirst:
                    playIndexes = [i for i in playIndexes if hartThree in i]
                playIndexesDict[playType] = playIndexes[:]
            playIndexes,playType = self.getFlush(self.cards[:])
            if playIndexes:
                if isFirst:
                    playIndexes = [i for i in playIndexes if hartThree in i]
                playIndexesDict[playType] = playIndexes[:]
            playIndexes,playType = self.getContiThree(currentCards)
            if playIndexes:
                if isFirst:
                    playIndexes = [i for i in playIndexes if hartThree in i]
                playIndexesDict[playType] = playIndexes[:]
            playIndexes,playType = self.getPlane(currentCards)
            if playIndexes:
                if isFirst:
                    playIndexes = [i for i in playIndexes if hartThree in i]
                playIndexesDict[playType] = playIndexes[:]

        return playIndexesDict

    def playRandomByPreCards(self, preCardsType, preCards):
        '''
        从可出的牌堆里随机的选出一个，并删除相应的手牌
        '''
        playType = ''
        cardsCanPlay = []
        playIndexesDict = self.getCardsCanPlay(preCardsType, preCards)

        for type in playIndexesDict.keys():
            cardsCanPlay += playIndexesDict[type]

        playIndex = choice(cardsCanPlay)
        if playIndex == PASS:
            return {'cards': PASS, 'type': PASSTYPE}

        for type in playIndexesDict.keys():
            if playIndex in playIndexesDict[type]:
                playType = type
                break
        playCards = [self.cards[i] for i in playIndex]

        return {'cards': playCards, 'type': playType}

    def playRandom(self):
        '''
        从所有可打的牌里选一个出来
        '''
        playIndexesDict = self.getCardsCanPlay()
        playType = ''
        cardsCanPlay = []

        for type in playIndexesDict.keys():
            cardsCanPlay += playIndexesDict[type]

        playIndex = choice(cardsCanPlay)
        for type in playIndexesDict.keys():
            if playIndex in playIndexesDict[type]:
                playType = type
                break
        playCards = [self.cards[i] for i in playIndex]

        return {'cards': playCards, 'type': playType}

    def playCardsWithHart3(self):
        playIndexesDict = self.getCardsCanPlay()
        playType = ''
        cardsCanPlay = []

        hartThree = self.cards.index(HART3)

        for type in playIndexesDict.keys():
            for cards in playIndexesDict[type]:
                if hartThree in cards:
                    cardsCanPlay.append(cards)

        playIndex = choice(cardsCanPlay)
        for type in playIndexesDict.keys():
            if playIndex in playIndexesDict[type]:
                playType = type
                break
        playCards = [self.cards[i] for i in playIndex]

        return {'cards': playCards, 'type': playType}

    def playCards(self, preCards=None, preCardsType=''):
        '''
        按照规矩出牌
        打单支*                    SINGLE          1
        打对子* getPairs()         PAIR            2
        打三个头不带* getThree()    THREE           3  
        打炸弹* getBomb()          BOMB            3-4
        打连对* getContiPairs()    CONTIPAIR       4-
        打三带二* getThreeTwo()    THREETWO        5
        打顺子* getFlush()         FLUSH           5-
        打钢板* getContiThree()    CONTITHREE      6-
        打飞机* getPlane()         PLANE           8-
        '''
        playDict = {}

        # 打上家的牌
        if preCards:
            playDict = self.playRandomByPreCards(preCardsType, preCards)
        # 自己随意出牌的回合
        else:
            playDict = self.playRandom()
            
        playCards = playDict['cards']
        if playCards != -1:
            self.removeCards(playCards)
        return playCards, playDict['type']

    def playFirstCards(self):
        playDict = self.playCardsWithHart3()
        self.removeCards(playDict['cards'])
        return playDict['cards'], playDict['type']        


if __name__ == '__main__':
    p = Player('zyd')
    cards = ['5A', '5C', '5D', '5C', '4A', '4C', '4B', '4C', '6A', '6B', '6A', '6C', '9A', '7A', '7A', '9A']
    print cards
    currentCards = [int(card[0:-1]) for card in cards]
    print p.getPlane(currentCards, [4,4,4,5,5,5,4,5,3,3,3,6])
    # , [3,3,3,4,4,4,5,5,5,6,6,6,7,7,7,8]

    # print int('4') < 3

    # players = []
    # players.append(Player('zyd'))
    # players.append(Player('zwx'))
    # players.append(Player('znx'))
    # rf = RunFast(players)
    # for x in xrange(1,1000):
    #     rf.shuffle()
    #     rf.dealCards()
    #     rf.start()
    #     rf.reset()