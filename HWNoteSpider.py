#coding=utf8

import requests,json,html
from lxml import etree
import datetime,os,time

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

payload = json.dumps({
  "traceId": ""
})
header= {
  'Cookie': config.get('cookie', ''),
  'Content-Type': 'application/json'
}

# 解析所有笔记目录 JSON 数据
def getAllNote():
    try:
        response = requests.request("POST", list_url, headers=header, data=payload)
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
        
        # 请求笔记内容
        contentPayload = json.dumps({
            "ctagNoteInfo": "123",
            "ctagNoteTag": "123",
            "guid": guid,
            "startCursor":"123",
            "traceId": "123"
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

