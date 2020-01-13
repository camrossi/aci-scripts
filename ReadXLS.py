import pyexcel
import pyexcel_xlsx

sheet = pyexcel.load('/Users/camrossi/Downloads/ACICONFIG.xlsx', name_columns_by_row=0)
records = sheet.to_records()
switch_list = set()

for record in records:
    switch_list.add(record['TOR Switch'])

print switch_list
for switch in switch_list:
    for record in records:
        if record['Port Type'] == "Access" and record['TOR Switch'] == switch:
            print record
    print "NEW SWITCH"


print "Excell keys:", records[0].keys()