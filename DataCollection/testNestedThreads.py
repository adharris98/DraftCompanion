from threading import Thread
import time


def printThread(i, j):
    time.sleep(i+j)
    print(f'Currently in thread (parent,child): ({i},{j})')



def threadTest(i):
    threads2 = list()
    for j in range(4):
        t = Thread(target=printThread, args=(i,j))
        threads2.append(t)
        t.start()
    for t in threads2:
        t.join()


def main():
    threads = list()
    for i in range(2):
        t = Thread(target=threadTest, args=(i,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()


if __name__ == "__main__":
    main()