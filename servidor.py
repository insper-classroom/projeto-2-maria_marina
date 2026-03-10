from flask import Flask, request, redirect
app = Flask(__name__)
app.static_folder = 'static'

@app.route('/')
def index():
    pass

if __name__ == '__main__':
    app.run(debug=True)

# oi marina =)