import os
import openpyxl

def save_to_excel(data, filename='output/businesses.xlsx'):
    if not os.path.exists('output'):
        os.makedirs('output')
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.append(['Name', 'Address', 'Zipcode', 'Phone', 'Website', 'BusinessType'])
    for item in data:
        sheet.append([
            item['Name'], item['Address'], item['Zipcode'],
            item['Phone'], item['Website'], item['BusinessType']
        ])
    workbook.save(filename)
    print(f"[+] Saved {len(data)} businesses to {filename}")