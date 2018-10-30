# -*- coding: utf-8 -*-
"""
Created on Wed Sep 26 14:37:43 2018

@author: TWanasukaphun
"""

#!/usr/bin/python

import json
import pickle
from datetime import datetime
import requests
import time
#import the Beautiful soup functions to parse the data returned from the website
from bs4 import BeautifulSoup as bs
from datetime import datetime
import pandas as pd
import re, os, sys, csv
from dateutil.parser import parse

#%%
urls = pd.read_csv("__FILE PATH__",header = None)
keys = urls[0]

values = urls[1]
url_dict = dict(zip(keys,values))

#%%
def dump_to_json(myList,filename,i):
    data = json.dumps(myList,ensure_ascii=False)
    with open("__FILE PATH__\\%s_blogspot(%s).json"%(filename,i),"w", encoding='utf-8') as f:
        f.write(data)
    return
  
def scrape_post(soup,last_link,filename):
    try:
        title = soup.find('h3').text.replace('\n', ' ').replace('\t', ' ').strip()
    except AttributeError:
        title = "None"
    try:
        datescraped = soup.find('h2', class_='date-header').text.replace('\n', ' ').replace('\t', ' ').strip()
        date = parse(datescraped)
        date = date.strftime('%m/%d/%Y')+" 00:00:00"
    except AttributeError:
        date = "None"
    try:
        content = soup.find('div', class_='post-body entry-content') or soup.find('div', class_='post-body')
        body_text = content.text.replace('\n', ' ').replace('\t', ' ').strip()
    except AttributeError:
        body_text = "None"

    newdict = {
        'title': title,
        'date': date,
        'url': last_link,
        'text': body_text,
        'source': filename
        }
 
    main = soup.find('div',{'id':'post-outer'}) or soup.find('div',{'class':'widget Blog'}) 
    older = main.find('span', {'id': 'blog-pager-older-link'})

    if older is not None:
      new_link = older.find('a', href=True)['href']
      endloop = False
    else:
      print("Last post existing: {}\ndate: {}".format(title, date))
      new_link = None
      endloop = True
    return (newdict,new_link,endloop)
#%%
def get_post(last_link):
    r = requests.get(last_link, proxies=proxies,headers={'User-Agent': 'Mozilla/5.0'})
  
    if r.status_code == 200:
      c = r.content
      soup = bs(c, 'lxml')
      return (soup,r.status_code)
    else:
      print("Request error: {}".format(r.status_code))
      print("Save everything and exit")

      pass
    
    
    #%%

if __name__ == "__main__":
    global myList
    t0 = time.time()
    for a,each in enumerate(url_dict.keys()):
      list1 = []
      i = 0
      j = 0
      final_list = []
      filename = each
      url = url_dict[each]
      code_status = True
      while code_status:
          if i == 0:
            soup, status = get_post(url)
            newdict, next_post, endloop = scrape_post(soup,url,filename)
            list1.append(newdict)
            i += 1
          elif i > 0:
            soup1,status1 = get_post(next_post)
            if status1 == 200:
              print(status1)
              newdict, next_post,endloop = scrape_post(soup1,next_post,filename)
              if endloop == True:
                code_status = False
              else:
                code_status = True
                
              list1.append(newdict)
              i += 1

              if i % 1000 == 0:
                 dump_to_json(list1,filename,j)
                 list1 = []
                 j += 1
          else:
            continue

      dump_to_json(list1,filename,j)
      t1 = time.time()
      total_n = t1-t0
      print("Total seconds to run the script: {}".format(str(total_n)))

      