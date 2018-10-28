
![](http://p20tr36iw.bkt.clouddn.com/animal-17545_640.jpg)

<!--more-->

# 一起来相约猫眼

## 0.说在前面

之前有人给我提了个需求，让我去看看猫眼，字体反爬问题，我觉得有趣，因为之前没学过字体反爬。然后，就尝试去搞了一下，结果当时因为xx原因，放弃了。也是实力不够啊！后来，也就是昨天，又想起来了，这个遗留问题，就来尝试学习学习，本文将以猫眼专业版网站为例，深入研究字体反爬问题。

我们一起来学习吧，嗨啊嗨！



## 1.原理

> 网站:猫眼专业版
>
> https://piaofang.maoyan.com/?ver=normal

我想获取票房数据，结果看下图，没有数据。这就涉及到了字体反爬！

![](http://p20tr36iw.bkt.clouddn.com/maoyan_l.png)

我们暴力一波，直接用xpath解析，然后爬取出来的并不是想要的。。

然后我们来分析一下网页源码，看到style标签下面，有如下内容：

![](http://p20tr36iw.bkt.clouddn.com/woff.png)

我们看到，这个网站使用的是自定义字体，并且编码采用base64，我们来刷新一下页面，再看看一下当前的这个自定义字体位置，会发现，base64后面的字体编码内容是随机的，并不是固定的，最大的难点也在于这里！

我们将这里的d09开头到AAA结尾这一整块的字体编码复制出来，并通过python代码进行base64解码，并保存为maoyan.woff格式的字体。

这里介绍一个查看woff字体内部对应编码的网站：

> http://fontstore.baidu.com/static/editor/index.html

下图是我随机将woff文件打开后的样子！

![](http://p20tr36iw.bkt.clouddn.com/maoyan_font.png)

如上图，我们知道数字与编码对应关系为：

```python
"uniF1D0": "4","uniE13A": "3","uniE64F": "0","uniECF2": "1","uniF382": "2",
"uniE1FD": "8", "uniF5E4": "6","uniF1B0": "9","uniE71E": "7","uniE979": "5"
```

是不是，我们直接拿到了这个字体编码，然后根据字体编码匹配对应的数字，然后在爬出的数据中替换掉那些反爬字体就可以了呢？

答案是肯定的，但是这里要重点说明一下，**每次获取网站的数字与编码不会一样**！

仔细琢磨上面这句话，会发现矛盾了！

**编码是不固定**，不能用编码一一对应关系来处理字体反爬！

那么怎么做？这里才是**重重之中**！

引入第三方库`fontTools`，我们可以利用fontTools可以获取每一个**字符对象**。

这个对象你可以简单的理解为保存着这个字符的形状信息。而且编码可以作为这个对象的id，具有一一对应的关系。

**对象每次不会变化，我们可以根据对象中的编码属性获取编码所对应的数字**！

那么到这里，我们的整体思路就搞定了，总结一波！

首先我们随机从网站上获取原始的字体数据，然后对其base64进行解码，转为woff文件，通过上面的网站，手动匹配当前这个字体的编码与数字关系。对刚才建立的关系，通过`footTools`为编码与数字建立关系，由于对象是不变的，我们此时就不必考虑网站的编码与数字动态变化问题，只需要将编码塞进之前的footTools对象中，即可获取对应的数字！

这里再做解释，第一次我们取网站上的一个字体并解码为xx.woff，并得到映射关系，相应的编码相应的字体对象，而编码又与字体对应，反过来，当我们随机取得网上另外一个yy.woff字体时，我们知道了该字体的对象，那么我们可以通过对象与编码关系，得到编码，然后通过编码与字体关系，最终的得到我们想要的数字！

关系图如下：

```python
xx.woff 字体->编码->对象
yy.woff 字体->对象->编码->字体
```



下面我们来实战吧！

## 2.相约猫眼

> 导包

```python
import re
import base64
import requests
from lxml import etree
from fontTools.ttLib import TTFont
from prettytable import PrettyTable
```

> 封装---定义猫眼爬虫类

```python
class maoyanSpider():
    def __init__(self,url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
        }
        self.url = url
        self.headers = headers
```

> 获取网站源码

```python
def get_html(self):
    raw_html = requests.get(self.url, headers=self.headers).text
    return raw_html
```

> 存储字体

将字体存储为xml文件以及woff文件，这里填入自己在网站的上那一串字符！

```python
def save_xml(self):
    font = "填入网站上的base64后的一串字符"
    fontdata = base64.b64decode(font)
    with open("./maoyan.woff","wb") as f:
        f.write(fontdata)
    maoyan_fonts = TTFont('./maoyan.woff')
    maoyan_fonts.saveXML("text.xml")
```

> 对应关系

以我的woff为例，定义映射关系！

建立字体与编码关系：

```python
xx.woff 字体->编码->对象	
```

```python
def get_rel(self):
    maoyan_fonts = TTFont('./maoyan.woff')
    font_dict = {}
    base_num = {
        "uniF1D0": "4","uniE13A": "3","uniE64F": "0","uniECF2": "1","uniF382": "2",
        "uniE1FD": "8", "uniF5E4": "6","uniF1B0": "9","uniE71E": "7","uniE979": "5"}
    # 这里不明白的直接打印，获取到的是dict类型，编码与对象之间的关系
    # 得到对应字体的编码与对象关系
    _data = maoyan_fonts.getGlyphSet()._glyphs.glyphs
    for k, v in base_num.items():
        # 为对象建立字体编码关系！
        font_dict[_data[k].data] = v
    return font_dict
```

![](http://p20tr36iw.bkt.clouddn.com/maoyan_font.png)

> 获取网站实时编码字体对象

```python
def get_woff(self,html):
    selector = etree.HTML(html)
    font_text = selector.xpath('//style[@id="js-nuwa"]/text()')[0]
    base64_behind = re.split('\;base64\,', font_text)[1]
    font_content = re.split('\)', base64_behind)[0].strip()
    if font_content:
        bs_font = base64.b64decode(font_content)
        with open("new.woff",'wb') as f:
            f.write(bs_font)
    font_ttf = TTFont("new.woff")
    data = font_ttf.getGlyphSet()._glyphs.glyphs
    return data
```

> 将反爬的字体进行填充

有些数据是万，亿或者%结尾，那么得做判断！

查看网页源码，反爬虫字体为如下所示，以分号隔开，我们就是通过分号分割字符串，并建立循环，在循环中我们根据是否数据以`.`开头来判断是从3取还是4取，目的是取出后4为，将其与uni进行拼接即为我们上面woff字体文件中的编码！

然后通过`字体->对象->编码->字体`，最终获取真实字体，并返回真实字体！

```python
&#xe0b6;&#xf5f5;&#xef38;&#xe0b6;&#xe93f;.&#xedf8;万
```

```python
def replace_Str(self,str_r, data_woff):
    font_dict = self.get_rel()
    if str_r[-1] == "万" or str_r[-1] == "%"  or str_r[-1] == "亿" :
        str_end = str_r[-1]
        string = str_r.replace("万", '').replace("%", "").replace("亿", "")
        num_list = string.split(";")
        str_All = ""
        for each_str in num_list:
            if not each_str.startswith("."):
                each_str = each_str[3:].upper()
                if each_str:
                    each_str = font_dict[data_woff["uni%s" % each_str].data]
                    str_All+=each_str
            else:
                str_All+='.'
                each_str = each_str[4:].upper()
                each_str = font_dict[data_woff["uni%s" % each_str].data]

                str_All+=each_str

        str_All+=str_end
        return str_All
    else:
        str_list = str_r.split(";")
        str_All = ""
        for each_str in str_list:
            if each_str and not each_str.startswith("."):
                each_str = each_str[3:].upper()
                each_str = font_dict[data_woff["uni%s" % each_str].data]
                str_All+=each_str
            elif each_str:
                str_All += '.'
                each_str = each_str[4:].upper()
                each_str = font_dict[data_woff["uni%s" % each_str].data]
                str_All += each_str
        return str_All
```

> 数据抓取及美化打印

```python
    def get_content(self):
        html = self.get_html()
        data_woff = self.get_woff(html)
        selector = etree.HTML(html)
        dayStr = selector.xpath('//span[@id="dayStr"]/text()')[0].replace(' ','').replace('\n','')
        dapanStr = selector.xpath('//div[@class="logo"]/span[2]/text()')[0]
        total_Ticket = re.findall("<span id='ticket_count'><i class=\"cs\">(\S+)</i></span>", html)[0]
        total_Ticket = self.replace_Str(total_Ticket, data_woff)
        title_content =dayStr + dapanStr + total_Ticket

        dayTips = selector.xpath('//div[@id="dayTips"]/text()')[0]

        movie_name = selector.xpath('//li[@class="c1"]/b/text()')
        print(movie_name)
        time_ticket_list = []
        ticket_bili_list = []
        rank_bili_list = []
        site_bili_list = []
        for i in range(len(movie_name)):
            time_ticket = re.findall(r'<b><i class="cs">(\S+)</i></b>', html)[i]
            ticket_bili = re.findall(r'<li class="c3 "><i class="cs">(\S+)</i></li>', html)[i]
            rank_bili = re.findall(r'<li class="c4 ">[^.]+<i class="cs">(\S+)</i>[^.]+</li>', html)[i]
            site_bili = re.findall(r'<span style="margin-right:-.1rem">[^.]+<i class="cs">(\S+)</i>[^.]+</span>', html)[i]
            time_ticket_list.append(self.replace_Str(time_ticket, data_woff))
            ticket_bili_list.append(self.replace_Str(ticket_bili, data_woff))
            rank_bili_list.append(self.replace_Str(rank_bili, data_woff))
            site_bili_list.append(self.replace_Str(site_bili, data_woff))

        print(time_ticket_list)
        print(ticket_bili_list)
        print(rank_bili_list)
        print(site_bili_list)
        pt = PrettyTable()
        pt.add_column("片名",movie_name)
        pt.add_column("实时票房",time_ticket_list)
        pt.add_column("票房占比",ticket_bili_list)
        pt.add_column("排片占比",rank_bili_list)
        pt.add_column("上座率",site_bili_list)

        print(title_content)
        print(dayTips)
        print(pt)
```

![](http://p20tr36iw.bkt.clouddn.com/pre.png)

> 对比官网

![](http://p20tr36iw.bkt.clouddn.com/pre1.png)

