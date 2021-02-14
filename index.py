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
    try:
        png_file = styleanalysis.analyze(pgn_text,player_name,rating)
    except styleanalysis.PGNParseException:
        error_message = "PGNのパースに失敗しました。前のページに戻り、入力を再度行ってください。\nPGNファイルは2ゲーム以上を入力してください。" + "また、PGNファイルに含まれる名前と入力した名前が異なっていないかを確認してください。"
        return render_template('parseerror.html',title='PGN Parse Failed!',error_message=error_message)
        
    return render_template('analyze.html',title='Analyze',png_file=png_file)


if __name__ == "__main__":
        
    app.debug = False
    app.run()
