# coding: utf-8

import re
import base64
import requests
from lxml import etree
from fontTools.ttLib import TTFont
from prettytable import PrettyTable
class maoyanSpider():
    def __init__(self,url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
        }
        self.url = url
        self.headers = headers

    def get_html(self):
        raw_html = requests.get(self.url, headers=self.headers).text
        return raw_html

    def save_xml(self):
        font = "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"
        fontdata = base64.b64decode(font)
        with open("./maoyan.woff","wb") as f:
            f.write(fontdata)
        maoyan_fonts = TTFont('./maoyan.woff')
        maoyan_fonts.saveXML("text.xml")

    def get_rel(self):
        maoyan_fonts = TTFont('./maoyan.woff')
        font_dict = {}
        base_num = {
            "uniF1D0": "4","uniE13A": "3","uniE64F": "0","uniECF2": "1","uniF382": "2",
            "uniE1FD": "8", "uniF5E4": "6","uniF1B0": "9","uniE71E": "7","uniE979": "5"}
        _data = maoyan_fonts.getGlyphSet()._glyphs.glyphs
        # print(_data)
        for k, v in base_num.items():
            font_dict[_data[k].data] = v
        return font_dict

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

if __name__ == '__main__':
    url = 'https://piaofang.maoyan.com/?ver=normal'
    my = maoyanSpider(url)

    my.get_content()