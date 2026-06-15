import requests
import json

URL = "http://localhost:8001/counsel"

def test_1():
    try:
        resp = requests.post(URL, json={"message": "I got 90 percentile, OBC, ENTC, Pune"})
        data = resp.json()
        branches = data.get("profile", {}).get("branches", [])
        return branches
    except Exception as e:
        return str(e)

def test_2():
    try:
        r1 = requests.post(URL, json={"message": "90 percentile, obc, pune, cs"})
        r2 = requests.post(URL, json={"message": "90 PERCENTILE, OBC, PUNE, CS"})
        c1 = [c["collegeId"] for c in r1.json().get("colleges", [])]
        c2 = [c["collegeId"] for c in r2.json().get("colleges", [])]
        return "yes" if c1 == c2 and c1 else f"no ({c1} vs {c2})"
    except Exception as e:
        return str(e)

def test_3():
    try:
        resp = requests.post(URL, json={"message": "90 percentile, General, Pune, CS"})
        data = resp.json()
        chances = set(c.get("chance") for c in data.get("colleges", []))
        return list(chances)
    except Exception as e:
        return str(e)

def test_4():
    try:
        resp = requests.post(URL, json={"message": "90 percentile, General, Pune, CS"})
        data = resp.json()
        return len(data.get("colleges", []))
    except Exception as e:
        return str(e)

def test_5():
    try:
        resp = requests.post(URL, json={"message": "i got 90 percentile, OBC, ENTC, PUNE"})
        data = resp.json()
        prof = data.get("profile", {})
        colleges = data.get("colleges", [])
        if prof.get("district") == "Pune" and prof.get("category") == "GOBCS" and prof.get("branches") == ["EXTC"] and len(colleges) >= 8:
            return "working"
        else:
            return f"issues: {prof}, colleges: {len(colleges)}"
    except Exception as e:
        return str(e)

print(f"Test 1 ENTC: branches extracted = {test_1()}")
print(f"Test 2 case: same results yes/no = {test_2()}")
print(f"Test 3 reach: chance levels seen = {test_3()}")
print(f"Test 4 count: colleges returned = {test_4()}")
print(f"Test 5 full: working/issues = {test_5()}")
