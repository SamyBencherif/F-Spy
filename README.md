# F-Spy
A hacked together program that can track changes on your filesystem

Scan folder:

![](https://user-images.githubusercontent.com/10871454/115100543-538ae400-9f0b-11eb-9c5c-5d8e430fa5df.png)

Scan folder again after some change occurs on filesystem:

![](https://user-images.githubusercontent.com/10871454/115100541-52f24d80-9f0b-11eb-82f9-120429e7385b.png)

Use program to exactly locate file:

![](https://user-images.githubusercontent.com/10871454/115100542-538ae400-9f0b-11eb-90d7-435d5a617762.png)


I added in some visualizations to allow you to watch the programs progress--it's multithreaded.
BLUE = Scanned.
YELLOW = Scanning.
RED = This file has been modified since the last scan.
BLACK = Unscanned.
