import os
import datetime as dt


import datetime






# The format string for the strptime function
format_string = '%Y年%m月%d日 %I:%M:%S'

# The string to convert to a datetime object
string = '2023年4月27日星期四 下午8:40:59'

# Convert the string to a datetime object
datetime_object = datetime.datetime.strptime(string, format_string).replace(tzinfo=datetime.timezone(datetime.timedelta(hours=8)))

# Print the datetime object
print(datetime_object)

