import requests

url = 'http://localhost:8080/api/ranking/ranked-colleges'
params = {
    'percentile': 87,
    'category': 'GOBCS',
    'year': 2024,
    'capRound': 1,
    'priority': 'general'
}
resp = requests.get(url, params=params, timeout=15)
print('status', resp.status_code)
cols = resp.json()
print('total', len(cols))
for i, c in enumerate(cols[:20]):
    print(i, repr(c.get('branchName')), c.get('annualFee'), c.get('hostelAvailable'))
print('matching count', sum(1 for c in cols if any(br in c.get('branchName','').upper() for br in ['CS','IT']) and (c.get('annualFee') is None or c.get('annualFee') <= 96000) and c.get('hostelAvailable') is True))
