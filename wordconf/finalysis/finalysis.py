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
                          "\tEnum<String>    RepType([\"季报\",\"半年报\",\"年报\"]);//报告类型\n",
                          "\tNumeric    		BackTimes(0);	  //报告期	0当期1上一期 以此类推 \n",
                          "\tNumeric         dateshift(15);	  //报告偏移天数 比如季度报可能在统计日期之后15天才能拿到\n"
                          ]

        #if vartype[1] == "2d":
            #params_content.append("\tNumeric         index(0);//选择数据序号\n")
        #财务数据没有二维数据 不需要判断行数
        #变量定义段
        vars_content = ["Vars\n"]
        if vartype[1] == "1d":
            vars_content.append("\tDic<Array<" + vartype[0] + ">>\t\tMyVar(\"" + i["name"] + "\");\n")
        elif vartype[1] == "2d":
            vars_content.append("\tDic<Array<Array<" + vartype[0] + ">>>\t\tMyVar(\"" + i["name"] + "\");\n")
        vars_content.append("\tNatural Map<Integer,Numeric> date2DicTime;\n")
        #函数定义段
        defs_content = ["Defs\n",
                        "\tNumeric getcurdate(Numeric readdate,Numeric remaintimes)\n",
                        "\t{\n",
                        "\t\tNumeric repdate;\n",
                        "\t\tinteger baryear=YearFromDateTime(readdate);\n",
                        "\t\tinteger barmonth=MonthFromDateTime(readdate);\n",
                        "\t\tIf(RepType==\"年报\")\n",
                        "\t\t\trepdate=(baryear-1)*10000+1231;\n",
                        "\t\tElse if(RepType==\"半年报\")\n",
                        "\t\t{\n",
                        "\t\t\tNumeric temp=intpart((barmonth-1)/6);\n",
                        "\t\t\trepdate=iif(temp==0,baryear-1,baryear)*10000+iif(temp==0,12,6)*100+iif(temp==0,31,30);\n",
                        "\t\t}\n",
                        "\t\tElse If(RepType==\"季报\")\n",
                        "\t\t{\n",
                        "\t\t\tNumeric temp=intpart((barmonth-1)/3);\n",
                        "\t\t\trepdate=iif(temp==0,baryear-1,baryear)*10000+iif(temp==0,12,temp*3)*100+iif(temp<2,31,30);\n",
                        "\t\t}\n",
                        "\t\tif(remaintimes==0)\n",
                        "\t\t\tReturn repdate;\n",
                        "\t\tElse\n",
                        "\t\t\treturn getcurdate(repdate,remaintimes-1);\n",
                        "\t}\n"
                        ]
        #事件域正文段
        event_content = ["Events\n",
                         "\tOnReady()\n",
                         "\t{\n",
                         "\t\tRange[0:DataSourceSize()-1]\n",
                         "\t\t{\n",
                         "\t\t\tArray<Numeric> datearr;\n",
                         "\t\t\tGetDicTimeRange(MyVar,datearr,0,SystemDateTime);\n",
                         "\t\t\tNumeric i;\n",
                         "\t\t\tfor i=0 to GetArraySize(datearr)-1\n",
                         "\t\t\t{\n",
                         "\t\t\t\tArray<Numeric> tempvar;\n",
                         "\t\t\t\tif(GetDicValue(MyVar,datearr[i],tempvar))\n",
                         "\t\t\t\t{\n",
                         "\t\t\t\t\tdate2DicTime[intpart(utc2local(tempvar[0]))]=datearr[i];\n",
                         "\t\t\t\t}\n",
                         "\t\t\t}\n",
                         "\t\t}\n",
                         "\t}\n",
                         "\tOnBar(ArrayRef<Integer> indexs)\n",
                         "\t{\n",
                         "\t\tRange[0:DataSourceSize()-1]\n",
                         "\t\t{\n",
                         "\t\t\tArray<Numeric> tempvar;\n",
                         "\t\t\tNumeric dictime;\n",
                         "\t\t\tInteger repdate=IntPart(getcurdate(DateAdd(date,(-1)*dateshift),backtimes));\n",
                         "\t\t\tCommentary(\"repdate=\"+text(repdate));\n",
                         "\t\t\tif(MapFind(date2DicTime,repdate,dictime))\n",
                         "\t\t\t{\n",
                         "\t\t\t\tGetDicValue(MyVar,dictime,tempvar);\n",
                         "\t\t\t\tCommentary(\"读到的\"+text(utc2local(tempvar[0])));\n",
                         ]

        for j in range(len(i["subNames"])):
            temp_vartype = vartype[0]
            if "(numeric)" in i["subNames"][j]:
                #print(i["subNames"][j])
                temp_vartype = "numeric"
                i["subNames"][j] = i["subNames"][j].replace("(numeric)","")
                if vartype[1] == "1d":
                    event_content.append("\t\t\t\tPlot" + temp_vartype + "(\"" + i["subNames"][j].replace("_GBK","") + "\",Value(tempvar[" + str(j) + "]));\n")
                else:
                    event_content.append("\t\t\t\tPlot" + temp_vartype + "(\"" + i["subNames"][j].replace("_GBK","") + "\",Value(MyVar[0][index][" + str(j) + "]));\n")
            else:
                if vartype[1] == "1d":
                    event_content.append("\t\t\t\tPlot" + temp_vartype + "(\"" + i["subNames"][j].replace("_GBK","") + "\",tempvar[" + str(j) + "]);\n")
                else:
                    event_content.append("\t\t\t\tPlot" + temp_vartype + "(\"" + i["subNames"][j].replace("_GBK","") + "\",MyVar[0][index][" + str(j) + "]);\n")
            #replace去除"_GBK"
            #循环所有语句结束
        event_content.append("\t\t\t}\n")
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
        result.writelines(begin_content + params_content +  vars_content + defs_content + event_content + end_content)
        result.close()
