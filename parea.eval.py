import os

from dotenv import load_dotenv

from parea import Parea, trace
from parea.evals.general import levenshtein

load_dotenv()

p = Parea(api_key=os.getenv("PAREA_API_KEY"))


# annotate function with the trace decorator and pass the evaluation function(s)
@trace(eval_funcs=[levenshtein])
def greeting(name: str) -> str:
    return f"Hello {name}"

p.experiment(
    "Greetings",  # experiment name
    data=[
        { "name": "Foo", "target": "Hi Foo" },
        { "name": "Bar", "target": "Hello Bar" },
    ],  # test data to run the experiment on (list of dicts)
    func=greeting,
).run()
