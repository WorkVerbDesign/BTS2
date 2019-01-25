from blessings import Terminal
from datetime import datetime
import time

t = Terminal()

print(t.clear())
print(t.standout('hello there'))
print(t.bold_red_on_green('general kenobi'))

with t.location(0, t.height - 1):
    print('This is at the bottom.')

while 1:
    now = datetime.utcnow()
    print(t.move(12, 0) + t.clear_eol() + str(now))
    time.sleep(1)