def get_key(key):
    with open('secrets.txt','r') as file:
        for line in file:
            if line.startswith(key):
                return line.split('=',1)[1].replace("\n", "")
    return None