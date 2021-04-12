# -*- coding: utf-8 -*-


import os
import re
import sys
import signal
import time

from configparser import ConfigParser
from datetime import datetime
from dateutil.relativedelta import relativedelta
from termcolor import colored

from weboob.browser import LoginBrowser, URL, need_login
from weboob.browser.pages import HTMLPage, LoggedPage
from weboob.browser.filters.standard import CleanText
from weboob.exceptions import BrowserIncorrectPassword
from weboob.tools.json import json


class LoginPage(HTMLPage):
    def login(self, email, password):
        form = self.get_form()
        form['session[email]'] = email
        form['session[password]'] = password
        form.submit()
        return form['authenticity_token']


class AccountPage(LoggedPage, HTMLPage):
    pass


class LessonPage(LoggedPage, HTMLPage):
    def register(self):
        form = self.get_form()
        if '_method' in dict(form).keys():
            print(colored("# Already registered.", 'cyan'))
        else:
            print(colored("# Registered to lesson ! :-)", 'green'))
            form.submit()

    def is_registered(self, partner):
        for div in self.doc.xpath('//div[@class="lesson-participant-username"]'):
            if partner in CleanText('.')(div):
                return True
        return False


class NobleartBrowser(LoginBrowser):
    BASEURL = 'https://membres.temple-nobleart.fr'

    login = URL('/login', '/sessions', LoginPage)
    account = URL('/account', AccountPage)
    lesson = URL('/lessons/(?P<lesson_id>\d+)',
                 '/lessons.json', LessonPage)

    def location(self, *args, **kwargs):
        r = super(NobleartBrowser, self).location(*args, **kwargs)
        print("# Now on %s" % self.url)
        return r

    def do_login(self):
        token = self.login.go().login(self.username, self.password)

        if self.login.is_here():
            raise BrowserIncorrectPassword()

        self.session.headers['x-csrf-token'] = token
        self.session.headers['x-requested-with'] = "XMLHttpRequest"

    def get_lessons(self):
        start = datetime.now().strftime('%Y-%m-%d') 
        end = (datetime.now() + relativedelta(days=5)).strftime('%Y-%m-%d')
        timestamp = int(round(time.time() * 1000))
        params = {'start': start,'end': end, '_': timestamp, 'timezone': u"Europe/Paris"}
        return json.loads(self.location('lessons.json', params=params).content)

    def is_full(self, lesson_id):
        lesson = [x for x in self.get_lessons() if x['html_id'] == "lesson_%s" % lesson_id]
        return None if len(lesson) != 1 else lesson[0]['full_lesson']

    def check_timeslot(self):
        hour = int(datetime.now().strftime('%H'))
        if 2 < hour < 6:
            print(colored("# Night time ! Trying again in 10 minutes...", 'blue'))
            time.sleep(600)
            sys.exit(1)

    @need_login
    def register(self, lesson_id):
        self.check_timeslot()
        if self.is_full(lesson_id) is False:
            self.lesson.go(lesson_id=lesson_id)
            self.page.register()
        else:
            print(colored("# Lesson is full ! Trying again in 15 seconds...", 'yellow'))
            time.sleep(5)
            self.register(lesson_id)

    @need_login
    def show_lessons(self, name, is_coach=False):
        found = []
        for lesson in self.get_lessons():
            lesson_id = lesson['html_id'].split('_')[-1]
            coach = re.findall('Prof[^>]+.([\w\s-]+)', lesson['description'])[0]
            places_reserved, places_total = re.findall('\d+', lesson['description'])[-2:]

            if not is_coach:
                if int(places_reserved) == 0:
                    continue
                self.lesson.go(lesson_id=lesson_id)

            if (not is_coach and self.page.is_registered(name)) or (is_coach and name in coach):
                date = lesson['end'].split('T')[0]
                schedule = re.findall('(?<=>)[^\d]+(.+)', lesson['formatted_title'])[-1].replace('-', 'to')
                txt = "%s - %s - %s at %s" % (lesson['title'], coach, date, schedule)
                found.append({'id': lesson_id, 'txt': txt})

        name = "%s %s" % ("Coach" if is_coach else "Partner", name)
        if len(found):
            print(colored('# %s found in :' % name, 'green'))
            for lesson in found:
                print(colored('# Lesson #%s : %s' % (lesson['id'], lesson['txt']), 'cyan'))
        else:
            print(colored('# %s not registered in any lesson.' % name, 'red'))


def get_config():
    config = ConfigParser()
    config.read(os.path.dirname(os.path.abspath(sys.argv[0])) + '/config')
    return config


def signal_handler(signal, frame):
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, signal_handler)
    sys.setrecursionlimit(1000)

    config = get_config()
    email = config['credentials']['email']
    password = config['credentials']['password']

    b = NobleartBrowser(email, password)

    arg = sys.argv[1]
    if arg.isdigit():
        if len(arg) == 5:
            b.register(arg)
        else:
            print(colored("# Wrong id !", 'red'))
    else:
        b.show_lessons(sys.argv[1], is_coach=len(arg.split()) == 1)

if __name__ == '__main__':
    main()
