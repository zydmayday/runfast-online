# coding:utf-8
import os
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from uuid import uuid4
import pickle
from runFast import RunFast, Player
import time
from environment import RunFastEnvironment
from controller import RunFastNetwork
from agent import RunFastAgent


PLAY_WITH_AGENT = True

class CardGame(RunFastEnvironment):
    callbacks = []
    session_name_dict = {}
    PASSTYPE = 'PASS'

    def __init__(self):
        RunFastEnvironment.__init__(self)
        self.played_card_dict = {}

    def register(self, callback, session):
        self.callbacks.append({'session': session, 'callback': callback})
        print self.callbacks

    def unregister(self, callback):
        print len(self.callbacks), '-------------'
        session = ''
        player_name = ''
        remove_idx = 99
        for idx, c_dict in enumerate(self.callbacks):
            if c_dict['callback'] == callback:
                session = c_dict['session']
                player_name = self.session_name_dict[session]
                self.session_name_dict.pop(session)
                remove_idx = idx
        if len(self.callbacks) > remove_idx and player_name:
            self.callbacks.pop(remove_idx)
            player_idx = 99
            for idx, p in enumerate(self.players):
                if p.name == player_name:
                    player_idx = idx
            self.players.pop(player_idx)
            print 'pop player'

            # TODO 通知有人退出游戏
            self.notifyQuitedCallbacks(player_name)

    def notifyCallbacks(self):
        info = {}
        type = 'started'
        info['remain_cards'] = {}
        for p in self.players:
            info['remain_cards'][p.name] = p.getCurrentCards()
        if self.gameOver():
            type = 'over'
        for callback_dict in self.callbacks:
            player = self.getPlayer(self.session_name_dict[callback_dict['session']])
            info['type'] = type
            info['currentTurn'] = self.players[self.currentTurn].name
            info['currentCard'] = self.currentCard
            if self.whoPlayed != -1:
                info['whoPlayed'] = self.players[self.whoPlayed].name
            else:
                info['whoPlayed'] = ''

            info['cards'] = player.getCurrentCards()
            info['played_card_dict'] = self.played_card_dict
            callback_dict['callback'](info)

        if self.gameOver():
            self.reset()
            self.players = []
            self.played_card_dict = {}


    def move_to_next(self, playedCards, playedType):
        self.played_card_dict[self.players[self.currentTurn].name] = playedCards
        if self.PASSTYPE == playedType:
            self.passToNext()
        else:
            self.players[self.currentTurn].removeCards(playedCards)
            self.moveToNext(playedCards, playedType)

        self.notifyCallbacks()
        # for auto play
        if PLAY_WITH_AGENT:
            self.autoPlay()
            self.autoPlay()


    def start_game(self):
        self.currentTurn = self.chooseWhoStart()
        whoPlayedName = ''
        if self.whoPlayed != -1:
            whoPlayedName = self.players[self.whoPlayed].name
        for callback_dict in self.callbacks:
            player = self.getPlayer(self.session_name_dict[callback_dict['session']])
            player.sortCards()
            # info = {'type': 'started', 'cards': player.getCurrentCards()}
            info = {'type': 'started','currentTurn': self.players[self.currentTurn].name, 'currentCard': self.currentCard, 'whoPlayed': whoPlayedName, 'cards': player.getCurrentCards(), 'played_card_dict': []}
            callback_dict['callback'](info)
        print 'game started'
        # for auto play
        if PLAY_WITH_AGENT:
            while self.players[self.currentTurn].name == 'random1' or self.players[self.currentTurn].name == 'random2':
                self.autoPlay()
            


    def notifyJoinedCallbacks(self, name):
        '''
        推送消息，玩家加入游戏
        '''
        info = {'type': 'waiting', 'playername': name}
        for callback_dict in self.callbacks:
            callback_dict['callback'](info)

    def notifyQuitedCallbacks(self, name):
        '''
        推送消息，玩家离开游戏
        TODO
        '''
        info = {'type': 'quited', 'playername': name}
        for callback_dict in self.callbacks:
            callback_dict['callback'](info)

    def autoPlay(self, agent=None):
        '''
        用在一个人玩的时候，提供两个电脑进行对战
        '''
        # time.sleep(3)
        currentTurn = self.currentTurn
        whoPlayed = self.whoPlayed
        preCards = self.currentCard
        preType = self.currentType
        player = self.players[currentTurn]
        # cards_dict = {}
        # if self.agent:
        state = self.getState()
        cards_dict = player.getBestAction(state)
        # else:
        #     if currentTurn == whoPlayed:
        #         cards_dict = self.players[currentTurn].playRandom()
        #     elif whoPlayed == -1:
        #         cards_dict = self.players[currentTurn].playCardsWithHart3()
        #     else:
        #         cards_dict = self.players[currentTurn].playRandomByPreCards(preType, preCards)
        playedCards = cards_dict['cards']
        playedType = cards_dict['type']
        self.players[currentTurn].removeCards(playedCards)
        self.played_card_dict[self.players[currentTurn].name] = playedCards
        if self.PASSTYPE == playedType:
            self.passToNext()
        else:
            self.moveToNext(playedCards, playedType)
        print 'auto play', playedCards, playedType
        self.notifyCallbacks()
        # return playedCards, playedType
        # self.move_to_next(playedCards, playedType)

class MainHandler(tornado.web.RequestHandler):

    def get(self):
        session = uuid4()
        players = self.application.game.players
        if len(players) == 3:
            # self.redirect('/board_status')
            self.finish('full')
        else:
            self.render('index.html', title='index', session=session)

    def post(self):
        '''
        加入游戏
        '''
        session = self.get_argument('session')
        game = self.application.game
        player_name = self.get_argument('player_name')
        game.session_name_dict[session.replace('-', '_')] = player_name

        if not session:
            self.set_status(400)
            return 

        players = self.application.game.players
        player_len = 3
        if PLAY_WITH_AGENT:
            player_len = 1
        if len(players) == player_len:
            self.finish('full')
        else:
            players.append(Player(player_name))
                
            game.notifyJoinedCallbacks(player_name)
            if len(players) == player_len:
                if PLAY_WITH_AGENT:
                    f = open('10000.nn')
                    nn = pickle.load(f)     
                    players.append(RunFastAgent('random1', nn))
                    players.append(RunFastAgent('random2', nn))
                game.shuffle()
                game.dealCards()
                self.render('card_board.html', msg='you have joined the game', players=players)
                game.start_game()
            else:
                self.render('card_board.html', msg='you have joined the game', players=players)

class PlayCardHandler(tornado.web.RequestHandler):
    '''
    出牌的handler
    '''

    def _checkLegal(self, cards, player_name):
        game = self.application.game
        currentTurn = game.currentTurn
        player = game.getPlayer(player_name)
        playerCards = player.getCurrentCards()
        currentCard = game.currentCard
        currentType = game.currentType
        cardsCanPlay = []
        # 如果是第一轮走牌，必须带红桃三
        if not currentCard:
            if '3A' not in cards:
                return False, cards, 'SINGLE'
        # 如果上一轮就是他走的话，那就重新走牌
        if currentTurn == game.whoPlayed:
            cardsCanPlay = player.getCardsCanPlay()
        else:
            cardsCanPlay = player.getCardsCanPlay(currentType, currentCard)

        playedCards = [playerCards.index(c) for c in cards]
        playedCards.sort()
        playedType = ''
        isLegal = False
        for type in cardsCanPlay.keys():
            for ccp in cardsCanPlay[type]:
                ccp.sort()
                if playedCards == ccp:
                    isLegal = True
                    playedType = type
                    break
        return isLegal, cards, playedType

    def get(self):
        pass

    def post(self):
        cards = self.get_arguments('cards[]')
        player_name = self.get_argument('player_name')

        isLegal, cards, playedType = self._checkLegal(cards, player_name)
        print player_name, isLegal, cards, playedType
        if isLegal:
            self.application.game.move_to_next(cards, playedType)
            self.finish('good')
        else:
            self.finish('illegal')

class BoardStatusHandler(tornado.websocket.WebSocketHandler):
    '''
    获取棋局的情况
    使用websocket
    '''
    def open(self):
        self.write_message('connected')

    def on_close(self):
        self.application.game.unregister(self.callback)

    def on_message(self, session):
        self.application.game.register(self.callback, session.replace('-', '_'))

    def callback(self, info):
        self.write_message(info)

class Application(tornado.web.Application):
    '''
    应用的主接口，用来配置一些基本的参数
    '''
    def __init__(self):  
        self.game = CardGame()

        handlers = {
            (r'/', MainHandler),
            (r'/play_card', PlayCardHandler),
            (r'/board_status', BoardStatusHandler),
        }

        settings = {
            'template_path': "templates",
            'static_path': "static",
        }

        tornado.web.Application.__init__(self, handlers, **settings)

if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = Application()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(8888 or os.environ['PORT'])
    tornado.ioloop.IOLoop.current().start()
