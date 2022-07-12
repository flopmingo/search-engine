from flask import Flask,request,render_template
from indexer import IndexSearch
app=Flask(__name__)

@app.route('/')
def my_form():
    return render_template('webui.html')

@app.route('/',methods=['POST'])
def my_form_post():
    text=request.form['u']
    obj=IndexSearch()
    urls = obj.searchIndex(text)
    
    url_str = ''
    for i in urls:
        url_str += str(i) + '<br/>'
    return url_str

if __name__ =="__main__":
    app.run()
