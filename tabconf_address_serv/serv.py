from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

submissions = []

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user = request.form.get('user')
        address = request.form.get('address')
        coordinate = request.form.get('coordinate')
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        submissions.append({
            'user': user, 
            'address': address, 
            'coordinate': coordinate,
            'timestamp': timestamp
        })
        return redirect(url_for('index'))
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html', submissions=submissions)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)