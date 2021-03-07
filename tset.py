import re
a = "1200万以下/月"
b = re.findall("[0-9]*-?[0-9]*",a)[0]
print(b)

