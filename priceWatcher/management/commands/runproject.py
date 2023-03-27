import os
import signal
from subprocess import Popen
from sys import stdin, stdout, stderr

from django.core.management import BaseCommand


class Command(BaseCommand):
    commands = [
        'python manage.py runKuCoin',
        'python manage.py runserver',
    ]
    help = 'Run all commands'

    def handle(self, *args, **options):
        proc_list = []

        for command in self.commands:
            print("$ " + command)
            proc = Popen(command, shell=True, stdin=stdin, stdout=stdout, stderr=stderr)
            proc_list.append(proc)

        try:
            while True:
                pass
        except KeyboardInterrupt:
            for proc in proc_list:
                os.kill(proc.pid, signal.SIGILL)
