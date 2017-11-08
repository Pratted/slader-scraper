# coding=utf-8
import sys
import json
import socket
import time
import os

#  Time to wait for JS to load on page and save.
DRYSCRAPE_TIMEOUT = 5
SLADER_DIR = "/home/eric/.slader/"

rows, columns = os.popen('stty size', 'r').read().split()


def json_path(isbn):
    isbn = str(isbn)
    return "%s%s/%s.json" % (SLADER_DIR, isbn, isbn)


def progress(count, total, suffix=''):
    bar_len = 40
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write((' ' * int(columns)) + '\r')
    sys.stdout.write('[%s] %s%s ...%s\r\n' % (bar, percents, '%', suffix))
    # sys.stdout.flush()  # As suggested by Rom Ruben


def load_json_doc(isbn):
    with open(json_path(isbn), 'r') as jsonfile:
        return json.load(jsonfile)


def save_json_doc(doc, isbn):
    with open(json_path(isbn), 'w') as outfile:
        json.dump(doc, outfile, indent=2)


def count_total_exercises(doc):
    count = 0
    for chapter in doc["toc"]:
        for section in chapter["sections"]:
            for exercise in section["exercises"]:
                if exercise["answers"]:
                    count += 1
    return count


def count_total_saved(doc):
    count = 0
    for chapter in doc["toc"]:
        for section in chapter["sections"]:
            for exercise in section["exercises"]:
                if exercise["answers"] and exercise["saved"]:
                    count += 1
    return count


def count_total_chapter_exercises(chapter):
    count = 0
    for section in chapter["sections"]:
        for exercise in section["exercises"]:
            if exercise["answers"]:
                count += 1

    return count


def count_total_chapter_saved(chapter):
    count = 0
    for section in chapter["sections"]:
        for exercise in section["exercises"]:
            if exercise["answers"] and exercise["saved"]:
                count += 1

    return count


def count_total_section_exercises(section):
    return len([1 for ex in section["exercises"] if ex["answers"]])


def count_total_section_saved(section):
    return len([1 for ex in section["exercises"] if ex["answers"] and ex["saved"]])


def scrape(isbn):
    doc = load_json_doc(isbn)
    overall_total = count_total_exercises(doc)
    overall_saved = count_total_saved(doc)

    for chapter in doc["toc"]:
        chapter_total = count_total_chapter_exercises(chapter)
        chapter_saved = count_total_chapter_saved(chapter)

        for section in chapter["sections"]:
            section_total = count_total_section_exercises(section)
            section_saved = count_total_section_saved(section)

            for ex in section["exercises"]:
                if not ex["saved"] and ex["answers"]:  # haven't saved this exercise and there are answers
                    if save_exercise(isbn, ex["url"], chapter["chapter"], section["id"], ex["id"], ex["answers"]):
                        overall_saved += 1
                        chapter_saved += 1
                        section_saved += 1
                        progress(overall_saved, overall_total, "Section " + section["id"])
                        progress(chapter_saved, chapter_total, section["topic"])
                        progress(section_saved, section_total, "Exercises %d / %d" % (section_saved, section_total))
                        sys.stdout.write((' ' * int(columns)) + '\r')
                        sys.stdout.write("Total %d / %d\r\n" % (overall_saved, overall_total))
                        sys.stdout.write("\033[F\033[F\033[F\033[F")  # Go to previous line.
                        ex["saved"] = True
                        save_json_doc(doc, isbn)


def save_exercise(isbn, url, chapter, section, exercise, solutions):
    import dryscrape

    if 'linux' in sys.platform:
        dryscrape.start_xvfb()

    chapter = chapter.strip().lower().replace(' ', '_')
    exercise = exercise.strip().replace('.', '')
    isbn = str(isbn)

    if not os.path.exists(SLADER_DIR + isbn):
        os.makedirs(SLADER_DIR + isbn)

    if not os.path.exists(SLADER_DIR + isbn + "/" + chapter):
        os.makedirs(SLADER_DIR + isbn + "/" + chapter)

    # /home/user/.slader/34564512443/chapter_6/6.1.2/png
    filename = "%s%s/%s/%s.%s.png" % (SLADER_DIR, isbn, chapter, section.strip(), exercise)
    js = open('simplify.js', 'r').read()

    try:
        session = dryscrape.Session()
        session.set_timeout(DRYSCRAPE_TIMEOUT)
        session.visit(url)
        session.eval_script(js)

        js = open('hide_all.js', 'r').read()
        session.eval_script(js)

        # toggle each solution on. take a screenshot. toggle off. repeat.
        for i in range(solutions):
            js = "document.getElementsByClassName(\"solution user-content\")[%d].style.visibility=\"visible\"" % i
            session.eval_script(js)
            session.render(filename.replace(".png", ".s%d.png" % i))
            js = "document.getElementsByClassName(\"solution user-content\")[%d].style.visibility=\"hidden\"" % i
            session.eval_script(js)

        time.sleep(1)
        return True
    except socket.error:
        #  "Connection refused. Exit to reset webkit."
        exit(1)
    except:
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: python slader.py <isbn>"

    script, isbn = sys.argv
    TEXTBOOK_DIR = SLADER_DIR + isbn + "/"

    scrape(int(isbn))
