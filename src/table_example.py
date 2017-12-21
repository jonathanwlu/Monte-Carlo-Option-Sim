import strike_table

if __name__ == '__main__':
    table = strike_table.CallPutTable(252, .25, 100, 10000, 125)
    table.export_to_csv()
