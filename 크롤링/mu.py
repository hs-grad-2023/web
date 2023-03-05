from bs4 import BeautifulSoup
import lxml
import requests
import csv
import re
import sqlite3
from sqlite3 import Error

class Musoup(): #기본 설정 객체
    def header(self): #접속을 위한 헤더값 바꾸기
        header={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                            'Chrome/104.0.0.0 Safari/537.36'}
        return header

    def m_get(self): #requests로 url주소에 get요청을 보내서 가져온 데이터를 text형식으로 저장
        site_url = 'https://www.musinsa.com/app/styles/lists?use_yn_360=&style_type=&brand=&model=&tag_no=&max_rt=&min_rt=&display_cnt=60&list_kind=big&sort=date&page={}'.format(start)
        print(site_url)
        test = requests.get(site_url, timeout=5, headers=mu_headers).text
        return test

    def m_soup(self, test): # text형식을 통해 가져온 html 문서를 lxml 파서를 통해서 BeautifulSoup 객체로 생성. soup는 해당 url의 모든 html 정보를 가짐
        soup = BeautifulSoup(test, 'lxml')
        return soup

def connection(): #sqlite3 연결
    try:
        conn = sqlite3.connect('musinsa.db')
        c = conn.cursor()
        return conn, c
    except Error:
        print(Error)

def create_mu(c): #sqlite 테이블 생성
    c.execute('''CREATE TABLE IF NOT EXISTS musinsa (
    item_text TEXT,
    item_title TEXT,
    item_model TEXT,
    item_picture TEXT,
    item_page TEXT
    )''')

def csvto_db(c): #csv파일 sqlite에 db로 저장
    with open(filename, 'r', encoding="utf-8-sig") as f:
        musin = csv.reader(f)
        next(musin)
        for row in musin:
            c.execute('INSERT INTO musinsa VALUES (?, ?, ?, ?, ?)', row)
    

def close(conn): #sqlite파일 변경사항 저장 및 닫기
    conn.commit()
    conn.close()


#기본 설정 객체 생성
musoup = Musoup()

#접속을 위한 헤더값 바꾸기
mu_headers = musoup.header()

#첫 번째 페이지 설정
start = 1

# csv파일로 저장
filename = "musinsa.csv"
f = open(filename, "w", encoding="utf-8-sig", newline="")
writer = csv.writer(f)

#csv에 타이틀 추가
title ="item_text item_title item_model item_picture item_page".split()
writer.writerow(title)

# link=[]
# link.append(soup.find(class_='paging-btn btn active'))
# link.extend(soup.find('div',class_='pagination').find_all('a', {'class':'paging-btn btn'}))
# link2 = [a.text for a in link]
# print(link2)


for _ in range(start, 10+1): # 최대 페이지 바꾸고 싶으면 숫자 바꾸기
    site_data = musoup.m_soup(musoup.m_get()).find_all('li', {'class':'style-list-item'})

    for it in site_data:
        item_info=[]
        item_info.append(it.select_one('.style-list-information__text').text) #text변환 인자를 더 설정하고 싶으면 .get_text()
        item_info.append(it.select_one('.style-list-information__title').text)
        item_info.append(it.select_one('.style-list-model').text)
        item_info.append('https:'+it.select_one('.style-list-thumbnail__img')['src']) #.get('src')도 가능
        item_info.append('https://www.musinsa.com/app/styles/views/'+re.sub(r'[\D]', '',it.select_one('.style-list-item__link')['onclick']))
        writer.writerow(item_info)
    start += 1

print("크롤링 끝!")

f.close() #파일 닫음

conn, c = connection()

create_mu(conn)

csvto_db(conn)

close(conn)
print("데이터베이스 저장완료!")

    
    
        

