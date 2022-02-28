import csv

#as always, something in my system changes the current dir to F:/Git


# with open("data.csv", "w") as file:
#     writer = csv.writer(file, lineterminator='\n') #lineterminator='\n' removes blank rows, but makes this code not *nix-compatible
#     writer.writerow(["transaction_id", "product_id", "price"])
#     writer.writerow([1000,1,5])
#     writer.writerow([1001,2,15])

t = {'aaa': 5, 'bbb':6}
for key, value in t.items():
    print(f'Key {key}')
    print(f'Value {value}')