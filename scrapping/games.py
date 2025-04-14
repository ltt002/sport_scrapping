from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
from datetime import datetime

app = FastAPI()


def get_mlb_results(input_date: str):
    today_date = datetime.today().strftime('%Y%m%d')
    if int(input_date) > int(today_date):
        return {"message": "還未到比賽日期"}

    url = f'https://www.playsport.cc/livescore.php?aid=1&gamedate={input_date}&mode=11'
    headers = {'User-Agent': ''}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return {"message": "連線失敗"}

    html_source = response.text
    soup = BeautifulSoup(html_source, 'html.parser')
    livescore_container = soup.find('div', id='livescoreContainer')

    if not livescore_container or '暫無資料' in livescore_container.text:
        return {"message": "沒有比賽數據"}

    games = []
    try:
        for game in soup.find_all('div', class_='js-gameOnbox'):
            team_a = game.get('data-namea', '未知隊伍').strip()
            team_h = game.get('data-nameh', '未知隊伍').strip()

            score_a = game.find('td', class_='big_score',
                                id=lambda x: x and x.endswith('_as_b'))
            score_h = game.find('td', class_='big_score',
                                id=lambda x: x and x.endswith('_hs_b'))
            score_a = score_a.text.strip() if score_a else '0'
            score_h = score_h.text.strip() if score_h else '0'

            innings_a = []
            innings_h = []
            for i in range(1, 10):
                inning_a = game.find(
                    'td', id=lambda x: x and x.endswith(f'_as{i}'))
                inning_h = game.find(
                    'td', id=lambda x: x and x.endswith(f'_hs{i}'))
                innings_a.append(inning_a.text.strip() if inning_a else '0')
                innings_h.append(inning_h.text.strip() if inning_h else '0')

            total_r_a = game.find('td', id=lambda x: x and x.endswith('_asr'))
            total_h_a = game.find('td', id=lambda x: x and x.endswith('_ash'))
            total_e_a = game.find('td', id=lambda x: x and x.endswith('_ase'))

            total_r_h = game.find('td', id=lambda x: x and x.endswith('_hsr'))
            total_h_h = game.find('td', id=lambda x: x and x.endswith('_hsh'))
            total_e_h = game.find('td', id=lambda x: x and x.endswith('_hse'))

            game_data = {
                'team_a': team_a,
                'team_h': team_h,
                'score_a': total_r_a.text.strip() if total_r_a else '0',
                'score_h': total_r_h.text.strip() if total_r_h else '0',
                'innings': {
                    'team_a': innings_a,
                    'team_h': innings_h
                },
                'total': {
                    'team_a': {
                        'R': total_r_a.text.strip() if total_r_a else '0',
                        'H': total_h_a.text.strip() if total_h_a else '0',
                        'E': total_e_a.text.strip() if total_e_a else '0'
                    },
                    'team_h': {
                        'R': total_r_h.text.strip() if total_r_h else '0',
                        'H': total_h_h.text.strip() if total_h_h else '0',
                        'E': total_e_h.text.strip() if total_e_h else '0'
                    }
                }
            }

            games.append(game_data)
    except Exception as e:
        return {"error": f"發生錯誤: {e}"}

    return {"games": games}


def get_nba_results(input_date: str):
    today_date = datetime.today().strftime('%Y%m%d')
    if int(input_date) > int(today_date):
        return {"message": "還未到比賽日期"}

    url = f'https://www.playsport.cc/livescore.php?aid=3&gamedate={input_date}&mode=11'
    headers = {'User-Agent': ''}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return {"message": "連線失敗"}

    html_source = response.text
    soup = BeautifulSoup(html_source, 'html.parser')
    livescore_container = soup.find('div', id='livescoreContainer')

    if not livescore_container or '暫無資料' in livescore_container.text:
        return {"message": "沒有比賽數據"}

    games = []
    try:
        for game in soup.find_all('div', class_='js-gameOnbox'):
            team_a = game.get('data-namea', '未知隊伍').strip()  # 客隊
            team_h = game.get('data-nameh', '未知隊伍').strip()  # 主隊

            score_a = game.find('td', class_='big_score',
                                id=lambda x: x and x.endswith('_asr_big'))
            score_h = game.find('td', class_='big_score',
                                id=lambda x: x and x.endswith('_hsr_big'))
            score_a = score_a.text.strip() if score_a else '0'
            score_h = score_h.text.strip() if score_h else '0'

            # 每局得分
            innings_a = []
            innings_h = []
            for i in range(1, 6):  # NBA最多5局
                inning_a = game.find(
                    'td', id=lambda x: x and x.endswith(f'_as{i}'))
                inning_h = game.find(
                    'td', id=lambda x: x and x.endswith(f'_hs{i}'))
                innings_a.append(inning_a.text.strip() if inning_a else '')
                innings_h.append(inning_h.text.strip() if inning_h else '')

            # R, T, L (總得分、加總、分差)

            total_r_a = game.find('td', id=lambda x: x and x.endswith('_asr'))

            total_r_h = game.find('td', id=lambda x: x and x.endswith('_hsr'))

            total_t = game.find('td', id=lambda x: x and x.endswith('_ts'))
            total_l = game.find(
                'span', id=lambda x: x and x.startswith('js-leadingpoint-'))

            game_data = {
                'team_a': team_a,
                'team_h': team_h,
                'score_a': total_r_a.text.strip() if total_r_a else '0',
                'score_h': total_r_h.text.strip() if total_r_h else '0',
                'innings': {
                    'team_a': innings_a,
                    'final_a': total_r_a.text.strip() if total_r_a else '0',
                    'team_h': innings_h,
                    'final_h': total_r_h.text.strip() if total_r_h else '0'
                },
                'summary': {
                    'total_score': total_t.text.strip() if total_t else '0',
                    'leading_point': total_l.text.strip() if total_l else 'N/A',
                }
            }

            games.append(game_data)
    except Exception as e:
        return {"error": f"發生錯誤: {e}"}

    return {"games": games}


@app.get("/mlbgames/{date}")
def get_games(date: str):
    return get_mlb_results(date)


@app.get("/nbagames/{date}")
def get_games(date: str):
    return get_nba_results(date)


@app.get("/")
def home():
    return {"message": "歡迎使用比賽數據API，請使用 /nbagames/{date}, 或/mlbgames/{date} 來查詢特定日期的比賽數據"}

# http://127.0.0.1:8000/mlbgames/20250324
# http://127.0.0.1:8000/nbagames/20250324
# bash uvicorn games:app --host 0.0.0.0 --port 8000 --reload
