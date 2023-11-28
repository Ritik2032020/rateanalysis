import csv
import matplotlib.pyplot as plt
import numpy as np

def load_csv_data(file_path):
    data = []
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)
    return data

def find_lcr(data, country=None, operator=None):
    filtered_data = data

    if country is not None:
        country_ids = {str(country)} if country is not None else set()
        filtered_data = [row for row in filtered_data if row['CountryId'] in country_ids]

    if operator is not None:
        operator_ids = {int(operator)} if operator is not None else set()
        filtered_data = [row for row in filtered_data if int(row['OperatorId']) in operator_ids]

    if not filtered_data:
        return None  # Return None if there are no results

    lcr_results = {}
    for row in filtered_data:
        key = (row['CountryId'], int(row['OperatorId']))  # Convert OperatorId to int
        rate = float(row['Rate'])
        if key not in lcr_results or rate < lcr_results[key]['rate']:
            lcr_results[key] = {'rate': rate, 'vendors': []}
        lcr_results[key]['vendors'].append({'VendorId': row['VendorId'], 'Rate': rate})

    for key, result in lcr_results.items():
        result['vendors'] = sorted(result['vendors'], key=lambda x: x['Rate'])[:3]

    return lcr_results


def find_lcr_for_plot(data, country=None, operator=None):
    filtered_data = data

    if country is not None:
        country_ids = {str(country)} if country is not None else set()
        filtered_data = [row for row in filtered_data if row['CountryId'] in country_ids]

    if operator is not None:
        operator_ids = {int(operator)} if operator is not None else set()
        filtered_data = [row for row in filtered_data if int(row['OperatorId']) in operator_ids]

    lcr_results = {}

    for row in filtered_data:
        key = (row['CountryId'], int(row['OperatorId']))  # Convert OperatorId to int
        rate = float(row['Rate'])
        if key not in lcr_results or rate < lcr_results[key]['rate']:
            lcr_results[key] = {'rate': rate, 'vendors': []}
        lcr_results[key]['vendors'].append({'VendorId': row['VendorId'], 'Rate': rate})

    lcr_results_for_plot = {}

    for key, result in lcr_results.items():
        vendor_data = result['vendors']
        # Sort the vendors by LCR rate in ascending order
        vendor_data.sort(key=lambda x: x['Rate'])
        top_3_vendors = vendor_data[:3]  # Limit to the top three vendors

        for vendor in top_3_vendors:
            vendor_id = vendor['VendorId']
            rate = vendor['Rate']

            if vendor_id not in lcr_results_for_plot:
                lcr_results_for_plot[vendor_id] = {'values': [], 'country_operator': key}

            lcr_results_for_plot[vendor_id]['values'].append(rate)

    return lcr_results_for_plot

def create_lcr_bar_chart(csv_data, selected_country=None, selected_operator=None):
    lcr_results = find_lcr(csv_data, country=selected_country, operator=selected_operator)

    if lcr_results:
        lcr_results_for_plot = find_lcr_for_plot(csv_data, country=selected_country, operator=selected_operator)
        vendor_ids = list(lcr_results_for_plot.keys())

        for vendor_id in vendor_ids:
            if 'values' not in lcr_results_for_plot[vendor_id]:
                lcr_results_for_plot[vendor_id]['values'] = []

        sorted_vendor_ids = sorted(vendor_ids, key=lambda vendor_id: np.mean(lcr_results_for_plot[vendor_id]['values']))

        lcr_values = [np.mean(lcr_results_for_plot[vendor_id]['values']) for vendor_id in sorted_vendor_ids]
        country_operators = [lcr_results_for_plot[vendor_id]['country_operator'] for vendor_id in sorted_vendor_ids]

        width = 0.35
        ind = np.arange(len(sorted_vendor_ids))

        fig, ax = plt.subplots()
        bars = ax.bar(ind, lcr_values, width, label='Mean LCR')

        ax.set_xlabel('Vendor ID')
        ax.set_ylabel('LCR')
        ax.set_title('LCR by Vendor')
        ax.set_xticks(ind)
        ax.set_xticklabels(sorted_vendor_ids)
        ax.legend()

        for i, bar in enumerate(bars):
            x = bar.get_x() + bar.get_width() / 2
            y = bar.get_height()
            country_operator = country_operators[i]
            top_3_values = sorted(lcr_results_for_plot[sorted_vendor_ids[i]]['values'])[:3]

            formatted_top_3_values = [f'{value:.5f}' for value in top_3_values]

            text = f"{country_operator}\nTop 3 LCR:\n{', '.join(formatted_top_3_values)}"
            ax.text(x, y / 2, text, ha='center', va='center', rotation=90, fontsize=8, color='black')

        plt.tight_layout()
        plt.show()
