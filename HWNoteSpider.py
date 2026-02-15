#coding=utf8

import requests,json,html
from lxml import etree
import datetime,os,time,re,random

list_url = "https://cloud.huawei.com/notepad/simplenote/query"
content_url = "https://cloud.huawei.com/notepad/note/query"

# 加载配置文件
config_path = os.path.dirname(os.path.abspath(__file__)) + "/config.json"
if os.path.exists(config_path):
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
else:
    print("错误: 找不到 config.json 配置文件。请复制 config.example.json 为 config.json 并填写配置。")
    exit(1)

cookie_str = config.get('cookie', '')

def get_cookie_value(key):
    match = re.search(f"{key}=([^;]+)", cookie_str)
    return match.group(1) if match else ""

user_id = get_cookie_value('userId')
csrf_token = get_cookie_value('CSRFToken')

def gen_trace_id():
    return f"03131_02_{int(time.time())}_{random.randint(10000000, 99999999)}"

header = {
    'Cookie': cookie_str,
    'Content-Type': 'application/json;charset=UTF-8',
    'CSRFToken': csrf_token,
    'userId': user_id,
    'x-hw-device-id': '91ee2ce0f294477f9d080af4abca066bf06b808d1df67eaa4e0bafaa2c55a0c8', # 使用抓包中的固定 ID
    'x-hw-device-category': 'Web',
    'x-hw-os-brand': 'Web',
    'x-hw-client-mode': 'frontend',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0',
    'Accept': 'application/json, text/plain, */*',
    'Origin': 'https://cloud.huawei.com',
    'Referer': 'https://cloud.huawei.com/home'
}

payload = json.dumps({
  "traceId": gen_trace_id()
})

# 解析所有笔记目录 JSON 数据
def getAllNote():
    try:
        # 每次获取列表使用新鲜的 traceId
        current_payload = json.dumps({"traceId": gen_trace_id()})
        response = requests.request("POST", list_url, headers=header, data=current_payload)
        result = json.loads(response.text)
        rsp_info = result.get('rspInfo')
        if not rsp_info:
            print(f"获取笔记列表失败: {response.text}")
            return None
        result_json = rsp_info.get('noteList')
        return result_json
    except Exception as e:
        print(f"请求笔记列表时发生错误: {e}")
        return None


if __name__ == '__main__':
    # 获取导出数量限制
    # None: 导出全部
    # 整数 (例如 10): 导出前 10 条
    EXPORT_LIMIT = config.get('export_limit')

    result_json = getAllNote()

    parsed_data = []
    if result_json:
        for j in result_json:
            data_str = j.get('data')
            if data_str:
                data = json.loads(data_str)
                parsed_data.append(data)

    # 按修改时间降序排序
    parsed_data.sort(key=lambda x: x.get('modified', 0), reverse=True)

    # 应用数量限制
    if EXPORT_LIMIT is not None:
        parsed_data = parsed_data[:EXPORT_LIMIT]

    all_notes = []

    for data in parsed_data:
        created_timestamp = data.get('created', 0)
        modified_timestamp = data.get('modified', 0)

        # 转换 Unix 时间戳
        try:
            created_time = datetime.datetime.fromtimestamp(created_timestamp/1000).strftime('%Y-%m-%d %H:%M:%S')
            modified_time = datetime.datetime.fromtimestamp(modified_timestamp/1000).strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            created_time = "未知"
            modified_time = "未知"

        guid = data.get('guid')
        if not guid:
            print("跳过 GUID 为空的笔记")
            continue
            
        print(f"正在处理笔记: {guid}")
        
        # 请求笔记内容 - 按照抓包数据修正 Payload
        contentPayload = json.dumps({
            "ctagNoteInfo": "",
            "startCursor": "102915",
            "guid": guid,
            "kind": "newnote",
            "traceId": gen_trace_id()
        })

        try:
            contentRes = requests.request("POST", content_url, headers=header, data=contentPayload)
            contentData = json.loads(contentRes.text)
            
            rsp_info = contentData.get('rspInfo')
            if not rsp_info:
                print(f"获取笔记内容失败 (GUID: {guid}): {contentRes.text}")
                continue
                
            t = rsp_info.get('data')
            if not t:
                print(f"笔记数据为空 (GUID: {guid})")
                continue
                
            content_json = json.loads(t)
            content_body = content_json.get('content')
            if not content_body:
                print(f"笔记正文为空 (GUID: {guid})")
                continue
                
            content_string = content_body.get('html_content', '')

            # 处理图片占位符
            imgList = content_json.get('fileList')
            if imgList != None and len(imgList) > 0:
                imgpos = 0
                while content_string.find('图片')!=-1 and imgpos < len(imgList):
                    content_string = content_string.replace('图片',imgList[imgpos].get('name'),1)
                    imgpos+=1

            t = html.unescape(content_string)
            html1=etree.HTML(t)
            result = html1.xpath('string(.)')
            
            note_entry = {
                "title": data.get('title'),
                "created_time": created_time,
                "modified_time": modified_time,
                "content": result
            }
            all_notes.append(note_entry)
            
            # 避免请求过快
            time.sleep(0.5)
            
        except Exception as e:
            print(f"处理笔记 {guid} 时发生异常: {e}")
            continue

    json_file = os.path.dirname(os.path.abspath(__file__)) + "/华为备忘录导出.json"
    with open(json_file, "w", encoding="utf8") as f:
        json.dump(all_notes, f, ensure_ascii=False, indent=4)
    print(f"导出完成，共计 {len(all_notes)} 条笔记。")

