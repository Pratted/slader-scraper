import os
import json
import requests
import bs4
import sys

from bs4 import BeautifulSoup
from slader import json_path
from slader import SLADER_DIR


def has_json_doc(isbn):
    filepath = "%s%s.json" % (TEXTBOOK_DIR, isbn)
    return os.path.exists(filepath)


def build_json_doc(isbn):
    url = "http://slader.com/textbook/%s" % isbn

    soup = BeautifulSoup(requests.get(url).text, 'lxml')

    try:
        title = soup.find_all('a', class_="textbook desktop")[0].text.strip()
        print "Found a textbook!"
        print "Title: %s" % title
        print "ISBN: %s" % isbn

        response = raw_input("Download this book? [Y/n] ")

        if response.lower()[0] == 'y':
            if not os.path.exists(TEXTBOOK_DIR):
                os.mkdir(TEXTBOOK_DIR)

            print "Building exercise list..."

            doc = {"isbn": isbn, "toc": load_toc(isbn)}

            with open(json_path(isbn), 'w') as outfile:
                json.dump(doc, outfile, indent=2)
        else:
            exit(1)
    except:
        print "Could not find a textbook for %s." % isbn
        exit(1)


def load_toc(isbn):
    url = "http://slader.com/textbook/%s" % isbn

    soup = BeautifulSoup(requests.get(url).text, 'lxml')
    toc = soup.find_all('section', class_="toc-item")

    return [load_chapter(chapter) for chapter in toc]


def load_chapter(chapter):
    sections = chapter.find_all('tr')
    chap = chapter.find_all('h3')[0].text  # Chapter #
    desc = chapter.find_all('p')[0].text  # Topic

    print chap + ": " + desc
    loaded = []
    for section in sections:
        num, topic, temp, start_page = section.find_all('td')
        print("Gathering section %s: %s" % (num.text, topic.text))
        start_page = int(start_page.text.strip().lower().replace('.', '').replace('p', '').replace('P', ''))
        loaded.append(load_section(section, num.text, topic.text, start_page))

    return {"desc:": desc, "chapter": chap, "sections": loaded}


def load_section(section, id, topic, start_page):
    base_url = "http://slader.com" + section.attrs['data-url']
    section = {"id": id, "topic": topic, "start_page": start_page, "exercises": []}

    page = start_page
    next_page = start_page

    #  Pages more than 1 page away are apart of the next section so don't include them.
    while next_page - page <= 1:
        soup = BeautifulSoup(requests.get(base_url).text, 'lxml')
        page = next_page
        next_page = int(soup.find(class_="next").text)
        base_url = "http://slader.com" + soup.find(class_="next").attrs['href']

        exercises = soup.find_all('section', class_='list')

        for p in exercises[0]:
            if isinstance(p, bs4.element.Tag) and p is not None:
                if 'data-url' in p.attrs:
                    url = "http://slader.com" + p.attrs['data-url']

                    num = p.find('span', class_='answer-number').text
                    num = str(num).replace('.', '')

                    try:
                        answers = int(p.find('span', class_="total-answers").find('strong').text)
                    except:
                        answers = 0

                    # print("Section %s: Exercise: %s " % (id, num))
                    section["exercises"].append({"id": num, "url": url, "saved": False, "answers": answers})

    return section


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: python setup_isbn.py <isbn>"

    script, isbn = sys.argv
    TEXTBOOK_DIR = SLADER_DIR + isbn + "/"

    if not has_json_doc(isbn):
        build_json_doc(isbn)
