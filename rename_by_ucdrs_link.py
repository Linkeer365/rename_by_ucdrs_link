import os
import re
import shutil

import time

import requests
from lxml import etree
import re

headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36"
}

book_dir=r"D:\AllDowns\newbooks"
already_buy_path=r"D:\compare_buy\already_buy.txt"

cnt=0

with open(already_buy_path,"r",encoding="utf-8") as f:
    links=[each.strip("\n") for each in f.readlines() if each!="\n"]

def get_check_digit(initpart):
    # https://wenku.baidu.com/view/b03803a59c3143323968011ca300a6c30c22f1cd.html
    if isinstance(initpart, int):
        initpart = str(initpart)
    assert len(initpart) == 12
    odd_place_digits = [int(val) for idx, val in enumerate(initpart, 1) if idx % 2 == 1]
    even_place_digits = [int(val) for idx, val in enumerate(initpart, 1) if idx % 2 == 0]
    weighted_sum = sum(odd_place_digits) * 1 + sum(even_place_digits) * 3
    # print("Weg Sum",weighted_sum)
    modOf10 = divmod(weighted_sum, 10)[1]
    check_digit = 10 - modOf10
    assert 0 <= check_digit <= 10
    # 强行归零
    if check_digit==10:
        check_digit=0
    return str(check_digit)

# print(get_check_digit("978780083741"))

def isbn10to13(isbn10):
    isbn12="978"+isbn10[:-1]
    check_digit=get_check_digit(isbn12)
    return isbn12+check_digit

print(isbn10to13("7540729295"))

def get_pack(ucdrs_url):
    # new_name = (title, isbn)
    # pack = (new_name, ss)
    global cnt
    cnt+=1
    print(f"第{cnt}本书")

    if cnt%20==0:
        time.sleep(2)

    page=requests.get(ucdrs_url).text
    html=etree.HTML(page)
    title_patt="//input[@name='orders.bookname']//@value"
    isbn_patt="//input[@name='isbn']//@value"
    ss_patt="//script[@language='JavaScript'][3]//text()"
    title=html.xpath(title_patt)

    if not title:
        return (None,None)

    title=title[0]
    title=re.sub("\s+","-",title)
    title=re.sub("/","",title)
    title=re.sub("\?","",title)

    isbn=html.xpath(isbn_patt)[0].replace("-","")

    if not isbn.isdigit():
        return (None,None)

    if len(isbn)==10:
        isbn=isbn10to13(isbn)

    ss_raw=html.xpath(ss_patt)[0]
    ss=re.findall("&ssn=(\d{8})&",ss_raw)

    if ss:
        ss=ss[0]
    else:
        return (None,None)

    new_name=f"{title}isbnisbn{isbn}"

    pack=(ss,new_name)

    print(f"tup:{pack}")

    return pack

def get_ss_from_filename(filename):
    ss=re.findall("1\d{7}",filename)
    if ss:
        print(f"ss:{ss}")
        return ss[0]
    else:
        print("ss:{}")
        return None

def main():
    ss_newnames=dict()
    for link in links:
        ss,newname=get_pack(link)
        ss_newnames[ss]=newname

    print()

    for book in os.listdir(book_dir):
        if book.endswith(".pdf"):
            ss=get_ss_from_filename(book)
            print(ss)
            print(ss_newnames)
            if ss in ss_newnames.keys() and ss!=None:
                newname=ss_newnames[ss]
                print("newname:",newname)
                if not os.getcwd()==book_dir:
                    os.chdir(book_dir)
                shutil.move(book,newname+".pdf")

    print("done.")

if __name__ == '__main__':
    main()


# get_pack("http://book.ucdrs.superlib.net/views/specific/2929/bookDetail.jsp?dxNumber=000004307749&d=A307516BA96F8398F3F1D893680275A9&fenlei=110305030101")