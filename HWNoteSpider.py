#coding=utf8

import requests,json,html
from lxml import etree
import datetime,os

list_url = "https://cloud.huawei.com/notepad/simplenote/query"
content_url = "https://cloud.huawei.com/notepad/note/query"
payload = json.dumps({
  "traceId": ""
})
header= {
  'Cookie': '填写你的cookie',
  'Content-Type': 'application/json'
}

#解析所有note目录json数据
def getAllNote():
    response = requests.request("POST", list_url, headers=header, data=payload)
    result = json.loads(response.text)
    result_json = result.get('rspInfo').get('noteList')
    return result_json


if __name__ == '__main__':
    # 设置导出数量限制
    # None: 导出全部
    # 整数 (例如 10): 导出前 10 条
    EXPORT_LIMIT = None 

    result_json = getAllNote()

    parsed_data = []
    if result_json:
        for j in result_json:
            data = json.loads(j.get('data'))
            parsed_data.append(data)

    # 按修改时间降序排序
    parsed_data.sort(key=lambda x: x.get('modified', 0), reverse=True)

    # 应用数量限制
    if EXPORT_LIMIT is not None:
        parsed_data = parsed_data[:EXPORT_LIMIT]

    all_notes = []

    for data in parsed_data:
        created_timestamp = data.get('created')
        modified_timestamp = data.get('modified')

        # 转换Unix时间戳
        created_time = datetime.datetime.fromtimestamp(created_timestamp/1000).strftime('%Y-%m-%d %H:%M:%S')
        modified_time = datetime.datetime.fromtimestamp(modified_timestamp/1000).strftime('%Y-%m-%d %H:%M:%S')

        guid = data.get('guid')
        print(guid)
        ##  request content
        contentPayload = json.dumps({
            "ctagNoteInfo": "123",
            "ctagNoteTag": "123",
            "guid": guid,
            "startCursor":"123",
            "traceId": "123"
        })

        contentRes = requests.request("POST", content_url, headers=header, data=contentPayload)
        # print(contentRes.text[0:100])
        contentData = json.loads(contentRes.text)
        # print(contentData)
        t = contentData.get('rspInfo').get('data')
        content_string = json.loads(t).get('content').get('html_content')

        #
        imgList = json.loads(t).get('fileList')
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

    json_file = os.path.dirname(os.path.abspath(__file__)) + "/华为备忘录导出.json"
    with open(json_file, "w", encoding="utf8") as f:
        json.dump(all_notes, f, ensure_ascii=False, indent=4)
