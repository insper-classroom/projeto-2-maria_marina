from flask import Flask, render_template_string, request, redirect
import views
app = Flask(__name__)
app.static_folder = 'static'

@app.route('/')
def index():
    return render_template_string(views.index())


if __name__ == '_main_':
    app.run(debug=True)

