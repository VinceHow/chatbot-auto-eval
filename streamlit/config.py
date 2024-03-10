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

traditional_metrics = ["faithfulness", "context_precision", "answer_relevancy", "context_recall"]

jobs_to_be_done_info = [
#   {
#     "job-to-be-done": "Discover new and unique snacks",
#     "need-and-motivation": "I want to expand my snacking horizons and try new flavors from around the world."
#   },
  {
    "job-to-be-done": "Simplify my snack shopping process",
    "need-and-motivation": "I want to save time and effort by having carefully curated snacks delivered to my doorstep."
  },
#   {
#     "job-to-be-done": "Find healthier snacking options",
#     "need-and-motivation": "I want to maintain a balanced diet without compromising on taste and variety."
#   },
 
#   {
#     "job-to-be-done": "Support small and artisanal snack brands",
#     "need-and-motivation": "I want to discover and support lesser-known snack makers who offer unique and high-quality products."
#   },
#   {
#     "job-to-be-done": "Manage my snack subscription easily",
#     "need-and-motivation": "I want the flexibility to pause, skip, or cancel my subscription according to my needs and preferences."
#   }
]