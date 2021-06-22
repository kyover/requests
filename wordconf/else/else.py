import json
import os

file_list = os.listdir("json/")
for filename in file_list:
    content = json.load(open("json/"+filename, "rb"), encoding="utf-8")  # 文件内容以list形式存储，列表第一个元素为总分类，需要删除
    del content[0]#删除第一个元素
    #对所有一级键名输出处理
    for i in content:
        #print(i["wordType"])
        result = open("txt/" + i["name"] + ".txt", "w")#新建公式txt文件
        vartype = i["wordType"].split("_")                  #vartype保存定义的数据类型
        #数据类型变换
        if vartype[0] == "double":
            vartype[0] = "Numeric"
        elif vartype[0] == "int":
            vartype[0] = "Numeric"
        elif vartype[0] == "string":
            vartype[0] = "String"
        #公式正文部分
        #nameDescription预处理,"-"替换成"_"
        i["nameDescription"] = i["nameDescription"].replace("-","_")
        begin_content = ["//------------------------------------------------------------------------\n",
                         "// 简称: " + i["name"] + "\n",
                         "// 名称: " + i["nameDescription"] + "\n",
                         "// 类别: 公式应用\n",
                         "// 类型: 内建应用\n",
                         "//------------------------------------------------------------------------\n"
                         ]
        #参数定义段
        params_content = ["Params\n",
                          "\tEnum<String>    BackType([\"基础数据回溯\",\"BAR回溯\"]);//回溯类型\n",
                          "\tNumeric         BackLength(0);//回溯周期\n"]

        if vartype[1] == "2d":
            params_content.append("\tNumeric         index(0);//选择数据序号\n")
        #变量定义段
        vars_content = ["Vars\n"]
        if vartype[1] == "1d":
            vars_content.append("\tDic<Array<" + vartype[0] + ">>\t\tMyVar(\"" + i["name"] + "\");\n")
        elif vartype[1] == "2d":
            vars_content.append("\tDic<Array<Array<" + vartype[0] + ">>>\t\tMyVar(\"" + i["name"] + "\");\n")
        #事件域正文段
        event_content = ["Events\n",
                         "    OnInit()\n",
                         "    {\n",
                         "        Range[0:DataCount()-1]\n",
                         "        {\n",
                         "            If(BackType == \"基础数据回溯\")\n",
                         "                SetDicFlag(MyVar, Enum_DicFlag_BackTime);\n",
                         "            Else If(BackType == \"BAR回溯\")\n",
                         "                SetDicFlag(MyVar, Enum_DicFlag_BackBar);\n",
                         "        }\n",
                         "    }\n",
                         "\n",
                         "    OnBar(ArrayRef<Integer> indexs)\n",
                         "    {\n",
                         "        Range[0:DataSourceSize()-1]\n",
                         "        {\n"
                         ]

        for j in range(len(i["subNames"])):
            temp_vartype = vartype[0]
            if "(numeric)" in i["subNames"][j]:
                #print(i["subNames"][j])
                temp_vartype = "numeric"
                i["subNames"][j] = i["subNames"][j].replace("(numeric)","")
                #print(i["subNames"][j])
                if vartype[1] == "1d":
                    event_content.append("\t\t\tPlot" + temp_vartype + "(\"" + i["subNames"][j].replace("_GBK","") + "\",Value(MyVar[BackLength][" + str(j) + "]));\n")
                else:
                    event_content.append("\t\t\tPlot" + temp_vartype + "(\"" + i["subNames"][j].replace("_GBK","") + "\",Value(MyVar[BackLength][index][" + str(j) + "]));\n")
            else:
                if vartype[1] == "1d":
                    event_content.append("\t\t\tPlot" + temp_vartype + "(\"" + i["subNames"][j].replace("_GBK","") + "\",MyVar[BackLength][" + str(j) + "]);\n")
                else:
                    event_content.append("\t\t\tPlot" + temp_vartype + "(\"" + i["subNames"][j].replace("_GBK","") + "\",MyVar[BackLength][index][" + str(j) + "]);\n")
            #replace("_GBK","")去除"_GBK"
            #循环所有语句结束
        event_content.append("\t\t}\n")
        event_content.append("\t}\n")

        end_content = ["//------------------------------------------------------------------------\n",
                       "// 编译版本	GS2021.04.16\n",
                       "// 版权所有	TradeBlazer Software 2003－2025\n",
                       "// 更改声明	TradeBlazer Software保留对TradeBlazer平\n",
                       "//			台每一版本的TradeBlazer公式修改和重写的权利\n",
                       "//------------------------------------------------------------------------"]
        #公式正文部分结束
        #写入文件
        result.writelines(begin_content + params_content +  vars_content + event_content + end_content)
        result.close()
