def logger(message,out=False):
    if out:
        print(message)
    with open('logs/log.txt', 'a') as f:
        f.write(message + " \n")
