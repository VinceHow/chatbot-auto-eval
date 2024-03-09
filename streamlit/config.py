import os 

def get_running_environment():
    if 'DYNO' in os.environ:
        print('This app is running on Heroku!')
        return "Heroku"
    else:
        print('This app is not running on Heroku.')
        return "Local"
    
local_url = "http://localhost:8501"
heroku_url = "https://chatbot-auto-eval-97fab36a4f1d.herokuapp.com"