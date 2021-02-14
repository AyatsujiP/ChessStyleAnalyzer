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

    filename = styleanalysis.analyze(pgn_text,player_name,rating)
    print(filename)
    return render_template('analyze.html',title='Analyze',filename=filename)


if __name__ == "__main__":
        
    app.debug = True
    app.run()
