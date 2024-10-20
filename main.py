from flask import Flask, request, render_template, jsonify
import requests

app = Flask(name)

def string_matching(a,b):
    if(b in a):
        return True
    return False

def get_data(api):
    response = requests.get(f"{api}")
    if response.status_code == 200:
        return response.json()
    else:
        return None

def contest_data(url):
    return get_data(url)

def updated_standings(contest_id, inp):
    contest_url = f"https://codeforces.com/api/contest.standings?contestId={contest_id}&from=1&count=9000&showUnofficial=false"
    contest_standings = contest_data(contest_url)

    if contest_standings is None:
        return None

    contestant = contest_standings['result']['rows']
    no_of_contestant = len(contestant)
    st = 1
    cont_lis = []

    while st <= no_of_contestant:
        handle_url = "https://codeforces.com/api/user.info?handles="
        for i in range(st, min(st + 700, no_of_contestant)):
            handle = contestant[i]['party']['members'][0]['handle']
            hndl = str(handle) + ";"
            handle_url += hndl

        cont_data = get_data(handle_url)
        if cont_data is None:
            break

        sz = len(cont_data['result'])

        for i in range(sz):
            cont_org = cont_data['result'][i]
            if cont_org.get('organization') is None:
                continue

            cont_org1 = cont_org['organization'].lower().replace(" ", "")
            for j in range(len(inp)):
                if string_matching(cont_org1, inp[j]):
                    cont_lis.append(contestant[i + st])
                    break

        st += 700

    return cont_lis

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        contest_id = request.form['contest_id']
        organizations = request.form['organizations'].split(',')

        organizations = [org.lower().replace(" ", "") for org in organizations]

        standings = updated_standings(contest_id, organizations)

        if standings:
            return render_template('result.html', standings=standings)
        else:
            return "Error fetching standings or no results."

    return render_template('index.html')

if name == 'main':
    app.run(debug=True)
