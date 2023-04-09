import time
import json
from config import cal_token, push_token
from homework_notification import get_cal_events, get_homework, ignoreSubmited, get_time_dl, get_hw_info,pushbullet_noti, save_json

while True:
    start_hour = time.time()
    print("Getting calendar events")
    clendar = get_cal_events(cal_token)
    hws_json = get_homework(clendar, 7)
    hws_json = ignoreSubmited(hws_json, push_token)

    while True:
        print('Opening pushes.json')
        with open('pushes.json', 'r') as f:
            pushes = json.load(f)

        for hw in hws_json:
            now = time.time()
            next_push = get_time_dl(hws_json[hw]['DL_TIME'].total_seconds())
            pushes[hw]['next_push'] = next_push
            print('next_push is:', next_push, end = ' ')
            print('now:', now, end = '')

            if pushes[hw]['lastPush'] != None:
                print('lastPush is not None', end = ' ')

                lastPush = pushes[hw]['lastPush']
                if next_push <= time.time() - lastPush:
                    title, body = get_hw_info(hw, hws_json)
                    pushbullet_noti(title, body, push_token)
                    pushes[hw]['lastPush'] = now
            else:
                print('lastPush is None', end = ' ')
                title, body = get_hw_info(hw, hws_json)
                pushbullet_noti(title, body, push_token)
                pushes[hw]['lastPush'] = now
        print('Saving pushes.json', pushes)
        save_json('pushes.json', pushes)
        print('Sleeping for 60 seconds')
        time.sleep(60)
        print('Donde sleeping')
        hws_json = ignoreSubmited(hws_json, push_token)
        end_hour = time.time()
        if end_hour - start_hour >= 3600:
            continue