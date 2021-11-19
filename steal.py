import argparse
from live_recorder import you_live
from live_recorder import version
import logging
import os
from datetime import datetime
import time

def parse_args():
    parser = argparse.ArgumentParser(prog='you-live', description="version %s : %s"%(version.__version__, version.__descriptrion__))
    parser.add_argument("liver", help="要录制的直播源，如 bili,douyu,kuaishou,acfun")
    parser.add_argument("id", help="要录制的房间号，可以从url中直接获取")
    parser.add_argument("-logfile", "-l", help="Log File", required=False, default=None)
    parser.add_argument("-qn", "-q", help="录制的清晰度，可以后续输入", required=False, default=None)
    parser.add_argument("-debug", help="debug模式", required=False, action='store_true', default=False)
    parser.add_argument("-check", help="校准时间戳", required=False, action='store_true', default=False)
    parser.add_argument("-delete", '-d', help="删除原始文件", required=False, action='store_true', default=False)
    parser.add_argument("-save_path", '-sp', help="源文件保存路径", required=False, default='./download')
    parser.add_argument("-check_path", '-chp', help="校正后的FLV文件保存路径", required=False, default=None)
    parser.add_argument("-format", '-f', help="文件命名格式", required=False, default='{name}-{shortId} 的{liver}直播{startTime}-{endTime}')
    parser.add_argument("-time_format", '-tf', help="时间格式", required=False, default='%Y%m%d_%H-%M')
    parser.add_argument("-cookies", '-c', help="cookie, 当cookies_path未指定时生效", required=False, default=None)
    parser.add_argument("-cookies_path", '-cp', help="指定cookie文件位置", required=False, default=None)
    parser.add_argument("-time_limit", '-tl', help="Max Record Time Length {10s}", required=False, default=10, type=float)
    parser.add_argument("-period", '-p', help="Query Cycle {120s}", required=False, default=120, type=float)
    
    args = parser.parse_args()
    
    if args.logfile is None:
        ts = datetime.now()
        args.logfile = 'logs/{}.log'.format(ts.strftime('%Y%m%d-%H%M%S'))
    if not os.path.exists(os.path.dirname(args.logfile)):
        os.makedirs(os.path.dirname(args.logfile))

    return args
    
def track_and_record(args):
    
    params = {}
    params['save_folder'] = args.save_path
    params['flv_save_folder'] = args.check_path
    params['delete_origin_file'] = args.delete
    params['check_flv'] = args.check
    params['file_name_format'] = args.format
    params['time_format'] = args.time_format
    params['cookies'] = args.cookies
    params['debug'] = args.debug
    params['time_limit'] = args.time_limit
   

    while True:
        recorder = you_live.Recorder.createRecorder(args.liver, args.id, **params)
         
        # 获取房间信息
        roomInfo = recorder.getRoomInfo()
        if args.debug:
            logging.debug(roomInfo)
            print(roomInfo)
         
        # 获取如果在直播，那么录制
        if roomInfo['live_status'] == '1':
            logging.info(roomInfo['live_rates'])
            smallest, qn = 100000, None
            for key in roomInfo['live_rates']:
                if int(key) < smallest:
                    smallest = int(key)
                    qn = key
            logging.info(f'Choosing resolution {qn}')
            print(f'Choosing resolution {qn}')
                 
            live_url = recorder.getLiveUrl(qn = qn)
            if args.debug:
                logging.debug(live_url)
            download_thread = you_live.DownloadThread(recorder)
            monitoring_thread = you_live.MonitoringThread(recorder)
            
            download_thread.start()
            monitoring_thread.start()
           
            download_thread.join()
            monitoring_thread.join()
            # convert into mp3
            #import moviepy.editor as me
            #clip = me.VideoFileClip('')
            #clip.audio.write_audiofile('*.mp3')
        else:
            logging.error('Stream Not Available Now')
            #print('Stream Not Available Now')
            time.sleep(args.period)


def main():
    args = parse_args()

    logging.basicConfig(filename=args.logfile)
    if args.cookies_path:
        try:
            with open(args.cookies_path,"r", encoding='utf-8') as f:
                params['cookies'] = f.read()
        except:
            logging.error(args.cookies_path)
            logging.error('指定cookie路径不存在')

    track_and_record(args)

if __name__ == '__main__':
    main()
