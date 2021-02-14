from flask import Flask,render_template
from flask import request
import styleanalysis

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', title='Chess Style Analyzer') #変更
    
@app.route('/analyze',methods=["POST"])
def analyze():
    pgn_text = str(request.form["pgn"])
    player_name = str(request.form["player_name"])
    rating = int(str(request.form["rating"]))

    png_file = styleanalysis.analyze(pgn_text,player_name,rating)
    return render_template('analyze.html',title='Analyze',png_file=png_file)


if __name__ == "__main__":
        
    app.debug = False
    app.run()
