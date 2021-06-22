import json
file = open("wordconf/系统-合约属性~TBG_CODEPROPERTY.json", "rb")
content = json.load(file, encoding="ytf-8")#文件内容以list形式存储，列表第一个元素为总分类，需要删除

del content[0]

for i in content:
    print(i["name"])
