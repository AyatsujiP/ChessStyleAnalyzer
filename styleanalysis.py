import sys,os,io
import base64

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns; sns.set()

import chess.pgn

import random, string

def randomname(n):
   randlst = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
   return ''.join(randlst)

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
    
    def sigmoid_for_adjustment(self,x):
        return 1/(2*(1+np.exp(0.007*(2550-x)))) + 0.2
    
    def adjust_draw_percentage(self,rating):
        GM_rating = 2700
        approximated_draw_rate = self.sigmoid_for_adjustment(rating)
        GM_draw_rate = self.sigmoid_for_adjustment(GM_rating)
        
        self.draw_percentage = self.draw_percentage - approximated_draw_rate + GM_draw_rate
        
    
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
    Alekhine_sd = {'Name': 'Alekhine', 'draw_percentage': 0.26071428571428573, 'piece_count_at_the_end': 15.595982142857142, 'middlegame_tendency': 0.1929611748458891}
    Botvinnik_sd = {'Name': 'Botvinnik', 'draw_percentage': 0.3920265780730897, 'piece_count_at_the_end': 15.803156146179402, 'middlegame_tendency': 0.0056127154060222435}
    Smyslov_sd = {'Name': 'Smyslov', 'draw_percentage': 0.5348511383537653, 'piece_count_at_the_end': 16.75936952714536, 'middlegame_tendency': -0.03822859275528381}
    Giri_sd = {'Name': 'Giri', 'draw_percentage': 0.48715858132898493, 'piece_count_at_the_end': 14.045250713412148, 'middlegame_tendency': 0.03717428837126662}
    Carlsen_sd = {'Name': 'Carlsen', 'draw_percentage': 0.38295421825511083, 'piece_count_at_the_end': 13.486610999136193, 'middlegame_tendency': 0.07825857432386059}
    Lasker_sd = {'Name': 'Lasker', 'draw_percentage': 0.23353819139596138, 'piece_count_at_the_end': 15.697980684811238, 'middlegame_tendency': 0.03981767915399228}
    Andersson_sd = {'Name': 'Andersson', 'draw_percentage': 0.6042003231017771, 'piece_count_at_the_end': 17.634248788368335, 'middlegame_tendency': -0.1662587246334225}
    Timman_sd = {'Name': 'Timman', 'draw_percentage': 0.4287856071964018, 'piece_count_at_the_end': 15.513493253373314, 'middlegame_tendency': -0.02731157577761788}
    Tal_sd = {'Name': 'Tal', 'draw_percentage': 0.4646978954514596, 'piece_count_at_the_end': 17.227427019687713, 'middlegame_tendency': -0.015291308693648083}
    So_sd = {'Name': 'So', 'draw_percentage': 0.46510656080234014, 'piece_count_at_the_end': 14.162139573756791, 'middlegame_tendency': 0.029006167155991486}
    Nepomniachtchi_sd = {'Name': 'Nepomniachtchi', 'draw_percentage': 0.3880281690140845, 'piece_count_at_the_end': 13.959154929577466, 'middlegame_tendency': 0.052706795209384476}
    Bronstein_sd = {'Name': 'Bronstein', 'draw_percentage': 0.4706860706860707, 'piece_count_at_the_end': 17.36881496881497, 'middlegame_tendency': 0.001659329625223538}
    Capablanca_sd = {'Name': 'Capablanca', 'draw_percentage': 0.31986809563066776, 'piece_count_at_the_end': 15.330585325638912, 'middlegame_tendency': 0.07142765955731484}
    
    Staunton_sd = {'Name': 'Staunton', 'draw_percentage': 0.13043478260869565, 'piece_count_at_the_end': 15.658385093167702, 'middlegame_tendency': 0.1778803001280134}
    Steinitz_sd = {'Name': 'Steinitz', 'draw_percentage': 0.19053708439897699, 'piece_count_at_the_end': 16.118925831202045, 'middlegame_tendency': 0.12134380745718325}
    Euwe_sd = {'Name': 'Euwe', 'draw_percentage': 0.34399052693901716, 'piece_count_at_the_end': 15.788632326820604, 'middlegame_tendency': 0.05342450556868281}
    
    Petrosian_sd = {'Name': 'Petrosian', 'draw_percentage': 0.5457858769931663, 'piece_count_at_the_end': 18.774487471526196, 'middlegame_tendency': -0.17944282165537367}
    
    Spassky_sd = {'Name': 'Spassky', 'draw_percentage': 0.5601229350749135, 'piece_count_at_the_end': 18.17018824433346, 'middlegame_tendency': -0.08694817456669778}
    Anand_sd = {'Name': 'Anand', 'draw_percentage': 0.4952635414136507, 'piece_count_at_the_end': 15.549186300704397, 'middlegame_tendency': -0.008019320194790732}
    
    Philidor_sd = {'Name': 'Philidor', 'draw_percentage': 0.13636363636363635, 'piece_count_at_the_end': 15.93939393939394, 'middlegame_tendency': -0.09952062684992309}
    Trifunovic_sd = {'Name': 'Trifunovic', 'draw_percentage': 0.6357798165137615, 'piece_count_at_the_end': 17.888073394495414, 'middlegame_tendency': -0.03304775629584045}
    Leko_sd = {'Name': 'Leko', 'draw_percentage': 0.5814882032667876, 'piece_count_at_the_end': 15.043557168784028, 'middlegame_tendency': 0.021804468134655513}
    
    ret = [Karpov_sd,Kasparov_sd,Fischer_sd,Kramnik_sd,Larsen_sd,Topalov_sd,
        Morphy_sd,Anderssen_sd,Alekhine_sd,Botvinnik_sd,Smyslov_sd,Giri_sd, Carlsen_sd,
        Lasker_sd,Andersson_sd,Timman_sd,Tal_sd,So_sd,Nepomniachtchi_sd,Bronstein_sd,
        Capablanca_sd,Staunton_sd,Steinitz_sd,Euwe_sd,Petrosian_sd,Spassky_sd,Anand_sd,
        Philidor_sd,Trifunovic_sd, Leko_sd]
    
    return ret

def show_scatterplot(ary):
    x = []
    y = []
    label = []
    for a in ary:
        x.append(a["draw_percentage"])
        y.append(a["middlegame_tendency"])
        label.append(a["Name"])

    h = sns.jointplot(x=x,y=y)

    h.ax_joint.set_xlabel('Draw Percentage',fontsize=20)
    h.ax_joint.set_ylabel('Middlegame/Endgame Tendency',fontsize=20)
    for i, txt in enumerate(label):
        h.ax_joint.text(x[i], y[i],txt,fontsize=14) 
    plt.show()

def save_scatterplot(ary):

    
    df = pd.DataFrame(data=ary)
    df["sep"] = [n if n == "you" else "GM" for n in df["Name"]]

    h = sns.jointplot("draw_percentage","middlegame_tendency",data=df,height=12.0,hue="sep")

    for key,row in df.iterrows():
        h.ax_joint.text(row["draw_percentage"], row["middlegame_tendency"],row["Name"],fontsize=14) 
    
   
    buffer = io.BytesIO()
    plt.savefig(buffer, format="PNG")
    
    base64Img = base64.b64encode(buffer.getvalue()).decode().replace("'", "")

    return base64Img

def create_sigmoid():
    #Approximation of https://en.chessbase.com/post/sonas-what-exactly-is-the-problem-
    x = np.arange(1500,2800,100)
    y = 1/(2*(1+np.exp(0.007*(2550-x)))) + 0.2

    print(x)
    print(y)


def analyze(pgn_text,player_name,rating=1800):
    with io.StringIO(pgn_text) as pgn:
        games, game_num = return_games(pgn)
        logger.info("Game Import Finished. Number of Games: %i " % game_num)
    
        player_side = check_player_side(games,player_name)
        #logger.debug("Check game side of %s: %s" % (args[2],str(player_side)))
        
        sd = StyleDescriptor(games,player_name)
        sd.create_style_descriptor()
        
        sd.adjust_draw_percentage(rating)
        
        sd_self = sd.return_style_descriptor()
        print(sd_self)
        ary = create_grandmaster_descriptor()
        ary.append(sd_self)
        filename = save_scatterplot(ary)    
        return filename

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
        
        show_scatterplot(ary)


if __name__ == "__main__":
    
    args = sys.argv
    print("/************************\nWelcome to StyleAnalyzer!\n/************************ \n\n")
    if not len(args) == 3 and not len(args) == 1:
        raise Exception("Usage: py -3 styleanalysis.py [pgnfile] [Player Name] ")
    
    if len(args) == 3:
        main(args)
    elif len(args) == 1:
        ary = create_grandmaster_descriptor()
        show_scatterplot(ary)