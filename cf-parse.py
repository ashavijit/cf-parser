# Built by Avijit Sen
# Date: 2020-05-01  
# License: MIT License
# Description: This script parses the Cloudflare logs and generates a report


import os
import sys
import json
import time
import requests
from bs4 import BeautifulSoup
import re
import shutil

#from macpath import join

parent_path=os.getcwd()
illegal_chars = ["<", ">", "[", "]",  "?", ":", "*" , "|"]


contest_url="https://codeforces.com/contests/with/"
username=input("Enter your Codeforces username: ")
submission_list_url='https://codeforces.com/submissions/{}/contest/'.format(username)
contest_url=contest_url+username

#visit the contest page
page=requests.get(contest_url,verify=True)
if(page.status_code!=200):
    print("Error: Could not fetch contest page: {}".format(contest_url))
    sys.exit(1)
soup=BeautifulSoup(page.content,'html.parser')

#extract data from the contest page

contests=soup.find('div',attrs={'class':'datatable'})
c_table=contests.find('tbody')
lst=c_table.find_all('tr')
total_contests=len(lst)-1
print("Total contests: {}".format(total_contests))
print("{} has participated in {} contests".format(username,total_contests))

def getExt(sub_lang):
    ext=" "
    if 'C++' in sub_lang:
        ext=".cpp"
    elif 'C' in sub_lang:
        ext=".c"
    elif 'Java' in sub_lang:
        ext=".java"
    elif 'Python' in sub_lang:
        ext=".py"
    elif 'Go' in sub_lang:
        ext=".go"
    elif 'Kotlin' in sub_lang:
        ext=".kt"
    elif 'Rub' in sub_lang:
        ext=".rb"
    elif 'PHP' in sub_lang:
        ext=".php"

    return ext


def createInfoFile(folder_name,username,info_arr):
    info_file=os.path.join(folder_name,"contest-info-on-{}.txt".format(username))
    flname=open(info_file,'a')
    txt_to_write=""
    for txt in info_arr:
        txt_to_write+=txt+"\n" #check1
    flname.write(txt_to_write)
    flname.close()

def createFolder(folder_name):
    if not os.path.exists(folder_name)==False:
        os.makedir(folder_name)
        print("Created folder: {}".format(folder_name))
        return 1
    else:
        print("Folder already exists: {}".format(folder_name))
        return 0


def info_arr_extr(row_data):
    info_arr=[]
    m_0= "contest no:"+row_data[0].text.strip()
    m_1= "contest name:"+row_data[1].find('a')['title'].strip()
    m_2 ="Rank :"  +row_data[3].find('a').text.strip()
    m_3= "Solved :" +row_data[4].find('a').text.strip()
    m_4= "Rating Change :" +row_data[5].find('span').text.strip()
    m_5= "New Rating :" +row_data[6].text.strip()
    m_user= "User :" +username

    info_arr.append(m_0)
    info_arr.append(m_1)
    info_arr.append(m_2)
    info_arr.append(m_3)
    info_arr.append(m_4)
    info_arr.append(m_5)
    info_arr.append(m_user)

    return info_arr

def make_dir_os(sub_id, contest_id, sub_status,sub_name,sub_lang, contest_name, get_soln,folder_name):
    ext=getExt(sub_lang)

    sub_name = sub_name+ext
    file_name=os.path.join(folder_name,sub_name)
    file1=open(file_name,'a')
    header="\n" + contest_id + " " + sub_id + " " + sub_status + " " + sub_lang + " " + contest_name + "\n" #check2
    file1.write(header+get_soln)
    file1.close()
def get_soln_text(sub_id, contest_id, sub_status,sub_name,sub_lang, contest_name,folder_name):
    url_soln = get_soln_url.format(contest_id,sub_id)
    print(url_soln)

    cpp = requests.get(url_soln, verify = True)
    soup_cpp = BeautifulSoup(cpp.text,'html.parser')
    
    get_soln = soup_cpp.findAll('div',attrs={"class" : "roundbox"})[1].find('pre').text
    make_dir_os(sub_id, contest_id, sub_status,sub_name,sub_lang, contest_name,get_soln,folder_name)


def extract_solution(row_data, c_id, contest_name,folder_name):
    # print(row_data)
    sub_cell = row_data[-3].find('span')
    sub_id = sub_cell['submissionid']
    sub_status = sub_cell.text
    sub_name = row_data[-5].find('a').text.strip()
    sub_lang =  row_data[-4].text.strip()
    
    #log
    print(sub_id)
    print(sub_status)
    print(sub_name)
    print(sub_lang)

    get_soln_text(sub_id,c_id,sub_status,sub_name,sub_lang, contest_name,folder_name)

    print("\n")


t = int(input('How many recent contests do you want to parse ?\nEnter : ')) + 1
get_soln_url = "http://codeforces.com/contest/{}/submission/{}"


for i in range(t):
    if i==0: continue 
    row = lst[i]
    row_data = row.findAll('td')

    #extract contest id
    info_arr = info_arr_extr(row_data)

    link = row_data[1]
    cname = link.find('a')['title']
    cnumber = link.find('a')['href']
    val = re.findall('[0-9]+',cnumber)[0] #regex

    sub_lst_url = submission_list_url + val

    #get all submissions for the contest
    new_page = requests.get(sub_lst_url, verify = True)
    if new_page.status_code !=200:
        print("This {} cannot be parsed !! ".format(cname))
        continue
    new_soup = BeautifulSoup(new_page.text,'html.parser')

    new_contests = new_soup.find('div', attrs={"class":"datatable"})
    new_sub_table = new_contests.find('tbody')
    new_lst = new_contests.findAll('tr')
    total_subs = len(new_lst) - 1

  
    cname = cname + " by User: {}".format(username)
    folder_name = os.path.join(parent_path,cname)
    os.chdir(parent_path)

    for str_char in illegal_chars:
        folder_name = folder_name[:10] + folder_name[10:].replace(str_char, " ")

    if createFolder(folder_name) == 0:
        continue

   
    print("\nTime to rest for 5 secs !!!\n")
    time.sleep(5)
       
    
    createInfoFile(folder_name,username,info_arr)   

    for i in range(len(new_lst)):
        if i == 0:continue
        new_row = new_lst[i]
        new_row_data = new_row.findAll('td')
        extract_solution(new_row_data, val, cname, folder_name)



# IF YOU LIKE THIS CODE, PLEASE UPVOTE IT ON CODEFORCES
# AVIJIT SEN
# GITHUB-ashavijit
#if (YOU_LIKE_THIS_CODE):
  #  UPVOTE_THIS_CODE()
#else:
# print("You can still upvote this code :P") 


