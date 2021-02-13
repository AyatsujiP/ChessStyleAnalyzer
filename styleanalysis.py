import sys,os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns; sns.set()

import chess.pgn

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(message)s')
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)


class StyleDescriptor():
    def __init__(self,games,player_name):
        self.draw_percentage = None
        self.piece_count_at_the_end = None
        
        self.player_name = player_name
        player_side_tmp = pd.Series(check_player_side(games,player_name))
        games_tmp = pd.Series(games)
        
        self.games = games_tmp[player_side_tmp != 99]
        self.player_side = player_side_tmp[player_side_tmp != 99]
        self.game_num = len(self.games)
        
        self.game_result = return_game_result(self.games,self.player_side)
    
    
    def create_style_descriptor(self):
        self.draw_percentage = self.return_draw_percentage()
        self.piece_count_at_the_end = self.return_piece_count_at_the_end()
        self.middlegame_tendency = self.return_corr_piece_count_and_win()
        
    
    def return_style_descriptor(self):
        ret = {"Name":"you","draw_percentage": self.draw_percentage,
               "piece_count_at_the_end": self.piece_count_at_the_end,
               "middlegame_tendency":self.middlegame_tendency}
               
        return ret
    
    def return_draw_percentage(self):
        draw_count = 0
        for game in self.games:
            if game.headers["Result"] == "1/2-1/2":
                draw_count += 1
        
        return draw_count /self.game_num
    
    def return_piece_count_at_the_end(self):
        """
        Returns Avg. Piece count at the end of the game.
        """
        piece_count = 0
        for game in self.games:
            end_node = game.end()
            end_board = end_node.board()
            piece_count += len(end_board.piece_map())
        
        return piece_count / self.game_num
    
    def return_corr_piece_count_and_win(self):
        piece_count = [0] * self.game_num
        for i,game in enumerate(self.games):
            end_node = game.end()
            end_board = end_node.board()
            piece_count[i] = len(end_board.piece_map())        
        
        return np.corrcoef(self.game_result,piece_count)[0,1]
    
def return_games(pgn):
    """
    Input: pgn(FileIO)
    Output: tuple(ret(list(chess.pgn.Game)),i(int))
    """
    ret = []
    i = 0
    while(True):
        game = chess.pgn.read_game(pgn)
        if not game is None:
            ret.append(game)
            i += 1
        else:
            break
    return (ret,i)

def return_game_result(games,player_side):
    """
    Input: games,player_side
    Output: If player wins or not
    """
    ret = [0] * len(games)
    for i,game in enumerate(games):
        if player_side.iat[i] == 1 and game.headers["Result"] == "1-0":
            ret[i] = 1
        elif player_side.iat[i] == 1 and game.headers["Result"] == "0-1":
            ret[i] = 0
        elif player_side.iat[i] == 0 and game.headers["Result"] == "0-1":
            ret[i] = 1
        elif player_side.iat[i] == 0 and game.headers["Result"] == "1-0":
            ret[i] = 0    
        else:
            ret[i] = 1/2
    
    return ret


def check_player_side(games,player_name):
    """
    Return Player Side of each game.
    1: White
    0: Black
    99: None
    """
    game_num = len(games)
    ret = [0] * game_num
    for i,game in enumerate(games):
        if player_name in game.headers["White"]:        
            ret[i] = 1
        elif player_name in game.headers["Black"]:
            ret[i] = 0
        else:
            ret[i] = 99
    return ret


def create_grandmaster_descriptor():
    Karpov_sd = {'Name': 'Karpov', 'draw_percentage': 0.44702970297029704, 'piece_count_at_the_end': 15.930445544554455, 'middlegame_tendency': -0.022937725748028093}
    Kasparov_sd = {'Name': 'Kasparov', 'draw_percentage': 0.3690922730682671, 'piece_count_at_the_end': 15.911102775693923, 'middlegame_tendency': 0.008122524089728179}
    Fischer_sd = {'Name': 'Fischer', 'draw_percentage': 0.3012295081967213, 'piece_count_at_the_end': 14.906762295081966, 'middlegame_tendency': 0.026533484962836116}
    Kramnik_sd = {'Name': 'Kramnik', 'draw_percentage': 0.4888002454740718, 'piece_count_at_the_end': 14.978827861307149, 'middlegame_tendency': 0.02969435805925698}
    Larsen_sd = {'Name': 'Larsen', 'draw_percentage': 0.31271609681137147, 'piece_count_at_the_end': 14.496350364963504, 'middlegame_tendency': 0.016312838284277226}
    Topalov_sd = {'Name': 'Topalov', 'draw_percentage': 0.4355089355089355, 'piece_count_at_the_end': 14.745920745920746, 'middlegame_tendency': 0.025765173185717465}
    Morphy_sd = {'Name': 'Morphy', 'draw_percentage': 0.10049019607843138, 'piece_count_at_the_end': 16.620098039215687, 'middlegame_tendency': 0.23115902467275062}
    Anderssen_sd = {'Name': 'Anderssen', 'draw_percentage': 0.11233480176211454, 'piece_count_at_the_end': 16.07819383259912, 'middlegame_tendency': 0.05981408001198815}
    
    ret = [Karpov_sd,Kasparov_sd,Fischer_sd,Kramnik_sd,Larsen_sd,Topalov_sd,Morphy_sd,Anderssen_sd]
    
    return ret

def show_scatterplot(ary):
    x = []
    y = []
    label = []
    for a in ary:
        x.append(a["draw_percentage"])
        y.append(a["middlegame_tendency"])
        label.append(a["Name"])
    """
    plt.title("Chess Player's Style Analyzer")
    plt.xlabel("Draw Percentage")
    plt.ylabel("Middlegame Tendency")
    plt.scatter(x,y)
    
    for i, txt in enumerate(label):
        plt.annotate(txt, (x[i], y[i]))
    
    plt.show()
    """
    h = sns.jointplot(x=x,y=y)

    h.ax_joint.set_xlabel('Draw Percentage',fontsize=20)
    h.ax_joint.set_ylabel('Middlegame/Endgame Tendency',fontsize=20)
    for i, txt in enumerate(label):
        h.ax_joint.text(x[i], y[i],txt,fontsize=16) 
    plt.show()


def create_sigmoid():
    #Approximation of https://en.chessbase.com/post/sonas-what-exactly-is-the-problem-
    x = np.arange(1500,2800,100)
    y = 1/(2*(1+np.exp(0.007*(2550-x)))) + 0.2

    print(x)
    print(y)

def main(args):
    with open(args[1],"r",encoding="utf-8") as pgn:
        games, game_num = return_games(pgn)
        logger.info("Game Import Finished. Number of Games: %i " % game_num)
    
        player_side = check_player_side(games,args[2])
        #logger.debug("Check game side of %s: %s" % (args[2],str(player_side)))
        
        sd = StyleDescriptor(games,args[2])
        sd.create_style_descriptor()
        sd_self = sd.return_style_descriptor()
        print(sd_self)
        ary = create_grandmaster_descriptor()
        ary.append(sd_self)
        
        show_scatterplot(ary)

if __name__ == "__main__":
    
    args = sys.argv
    print("/************************\nWelcome to StyleAnalyzer!\n/************************ \n\n")
    if not len(args) == 3:
        raise Exception("Usage: py -3 styleanalysis.py [pgnfile] [Player Name] ")
    main(args)
    