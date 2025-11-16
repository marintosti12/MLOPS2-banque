import cProfile, pstats, io, json, requests
from random import randint

payload = {
  "model_name": "lgbm_vanilla",
  "inputs": [
    {
      "SK_ID_CURR": i,
      "AMT_INCOME_TOTAL": 120000.0,
      "AMT_CREDIT": 300000.0,
      "AMT_ANNUITY": 15000.0,
      "CODE_GENDER":"M",
      "NAME_CONTRACT_TYPE":"Cash loans"
    } for i in range(256)
  ]
}

def bench():
    r = requests.post("http://localhost:8000/predict",
                      headers={"Content-Type":"application/json"},
                      data=json.dumps(payload))
    r.raise_for_status()

pr = cProfile.Profile()
pr.enable()
bench()
pr.disable()

s = io.StringIO()
ps = pstats.Stats(pr, stream=s).sort_stats("cumtime")
ps.print_stats(30)
print(s.getvalue())
