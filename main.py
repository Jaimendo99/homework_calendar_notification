import time
from config import cal_token, push_token
from homework_notification import get_cal_events, get_homework, ignoreSubmited, get_time_dl, get_hw_info,pushbullet_noti

while True:
    start_hour = time.time()
    clendar = get_cal_events(cal_token)
    hws_json = get_homework(clendar, 7)
    hws_json = ignoreSubmited(hws_json, push_token)

    while True:
        time.sleep(60)
        for hw in hws_json:
            now = time.time()
            next_push = get_time_dl(hws_json[hw]['DL_TIME'])
            hws_json[hw]['next_push'] = next_push

            try:
                lastPush = hws_json[hw]['lastPush']
                if next_push <= time.time() - lastPush:
                    title, body = get_hw_info(hw, hws_json)
                    pushbullet_noti(title, body, push_token)
                    hws_json[hw]['lastPush'] = now
                
            except KeyError:
                title, body = get_hw_info(hw, hws_json)
                pushbullet_noti(title, body, push_token)
                hws_json[hw]['lastPush'] = now
                
        hws_json = ignoreSubmited(hws_json, push_token)
        end_hour = time.time()
        if end_hour - start_hour >= 3600:
            continue