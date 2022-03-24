import requests, json, os
from bs4 import BeautifulSoup


def getAnswer(answers_dict, question_key, soup):
    correct_answer_number = answers_dict[question_key]['correct'].index(1) + 1
    correct_answer = soup.find('ul', {'data-question_id': question_key}).findNext('input', {
        'value': correct_answer_number}).next_sibling
    return correct_answer.strip()


def getHTML(url):
    return requests.get(url).text.encode('utf-16')


url = input('Введіть повну адресу теста:\n')
test_name = url[url.find('.info/')+6:-1]
whole_test_as_text = getHTML(url)
try:
    os.mkdir('tests')
    os.mkdir('output')
except FileExistsError:
    with open('tests/' + test_name + '.html', 'wb') as whole_test:
        whole_test.write(whole_test_as_text)
    with open('tests/' + test_name + '.html', 'rb') as whole_test:
        soup = BeautifulSoup(whole_test, 'html.parser')
        question_quantity = int(soup.find('span', {'class': 'wpProQuiz_correct_answer'}).findNext('span').text)
        for script in soup.findAll('script', {'type': 'text/javascript'}):
            if str(script).find('window.wpProQuizInitList = window.wpProQuizInitList || [];') != -1:
                for line in str(script).splitlines():
                    if 'json' in line:
                        answers_dict = json.loads(line[line.find('json:') + 5:-1 * (len(line) - line.rfind('}'))].strip())
    key_list = []
    text_list = []
    answer_list = []

    for i in soup.findAll('ul', {'class': 'wpProQuiz_questionList'}):
        question_key = i.get('data-question_id')
        key_list.append(question_key)
    for i in soup.findAll('div', {'class': 'wpProQuiz_question_text'}):
        question_text = i.find('p').text
        text_list.append(question_text)
    for i in range(0, question_quantity):
        answer_list.append(getAnswer(answers_dict, key_list[i], soup))

    with open('output/' + test_name + '.txt', "w") as outfile:
        outfile.write("Питання " + key_list[0] + '\n')
        outfile.write(text_list[0])
        outfile.write("\nВідповідь: " + answer_list[0] + "\n")
    for i in range(1, question_quantity):
        with open('output/' + test_name + '.txt', "a") as outfile:
            outfile.write("\nПитання " + key_list[i] + "\n")
            try:
                outfile.write(text_list[i])
            except UnicodeEncodeError:
                outfile.write("ВИНИКЛА ПОМИЛКА!\n" + text_list[i].encode("cp1251", 'ignore').decode("cp1251", 'ignore'))
            try:
                outfile.write("\nВідповідь: " + answer_list[i] + "\n")
            except UnicodeEncodeError:
                outfile.write("\nВИНИКЛА ПОМИЛКА!\nВідповідь: " + answer_list[i].encode("cp1251", 'ignore').decode("cp1251", 'ignore') + "\n")
