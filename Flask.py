#!/usr/bin/env python
# coding: utf-8

# app.run(debug=True)하면 에러가 남

# In[ ]:


from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return 'Hello, World!'

@app.route('/user')
def user():
    return 'Hello, User!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False, port=5001)


# In[ ]:




