import os
import pandas as pd
import base64
from io import BytesIO
import matplotlib.pyplot as plt
from django.shortcuts import render, redirect
from .forms import CSVUploadForm
from .models import CSVFile
from .models import Hotel
from django.shortcuts import render, get_object_or_404
from .forms import LocationSelectionForm
from django.http import HttpResponseRedirect
from django.urls import reverse
from .lcr_analysis import (
    load_csv_data,
    find_lcr,
    create_lcr_bar_chart,
)

def upload_csv(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('select_columns')
    else:
        form = CSVUploadForm()
    return render(request, 'csv_upload/upload_csv.html', {'form': form})

import matplotlib
matplotlib.use('Agg')


def select_columns(request):
    columns = []
    graph_type = 'bar'  # Default to 'bar' initially

    if request.method == 'POST':
        group_by_columns = request.POST.getlist('group_by')
        # print(group_by_columns)
        order_by_column = request.POST.get('order_by')

        # Get the column names from the CSV file
        csv_file = CSVFile.objects.last()
        # print(csv_file)
        if csv_file:
            df = pd.read_csv(csv_file.file.path)
            columns = df.columns.tolist()
            # print(columns)

            # Perform grouping
            if group_by_columns:
                grouped_data = df.groupby(group_by_columns, as_index=False)

                # Perform ordering if an order_by column is selected
                if order_by_column:
                    ordered_data = df.groupby(order_by_column).size().reset_index(name='count')

                    # Generate the bar graph using Matplotlib
                    plt.figure(figsize=(8, 6))
                    plt.bar(ordered_data[order_by_column], ordered_data['count'])
                    plt.xlabel(order_by_column)
                    plt.ylabel('Count')
                    plt.title(f'Bar Graph of {order_by_column}')
                    plt.xticks(rotation=45)

                    # Save the plot as an image in memory
                    buffer = BytesIO()
                    plt.savefig(buffer, format='png')
                    image_base64 = base64.b64encode(buffer.getvalue()).decode()
                    buffer.close()

                    # Update graph_type based on the user's selection
                    graph_type = request.POST.get('new_graph_type', 'bar')

                    # Pass the grouped data to the template
                    grouped_data = [group.to_dict(orient='records') for _, group in grouped_data]

                    return render(request, 'csv_upload/result.html', {'data': grouped_data, 'group_by': group_by_columns, 'order_by': order_by_column, 'columns': columns, 'image_base64': image_base64, 'graph_type': graph_type})
    #make changes in the system without makinfg any modification of the csv file 
    csv_file = CSVFile.objects.last()
    if csv_file:
        df = pd.read_csv(csv_file.file.path)
        columns = df.columns.tolist()

    return render(request, 'csv_upload/select_columns.html', {'columns': columns, 'graph_type': graph_type})


def select_hotel(request):
    # Get the last uploaded CSV file
    csv_file = CSVFile.objects.last()

    if csv_file:
        # Read the CSV data
        df = pd.read_csv(csv_file.file.path)
        
        # Check if the 'Location' column exists in your CSV file
        if 'Location' in df.columns:
            locations = df['Location'].unique()
            
            # Get the list of column names
            columns = df.columns.tolist()
            
            return render(request, 'csv_upload/select_hotel.html', {'locations': locations, 'columns': columns})
    
    return render(request, 'csv_upload/select_hotel.html', {'locations': [], 'columns': []})


def select_location(request):
    csv_file = CSVFile.objects.last()
    df = None

    if csv_file:
        df = pd.read_csv(csv_file.file.path)

    form = LocationSelectionForm(request.POST or None, df=df)

    if request.method == 'POST' and form.is_valid():
        selected_location = form.cleaned_data['location']
        print(f"Selected Location: {selected_location}") 
        
        if selected_location:
            # Filter the DataFrame to get hotel names associated with the selected location
            hotel_names = df[df['Location'] == selected_location]['Hotel Name'].unique()
        else:
            hotel_names = []  

       
        return render(request, 'csv_upload/hotel_results.html', {'selected_location': selected_location, 'hotel_names': hotel_names})

    return render(request, 'csv_upload/select_location.html', {'form': form})

def hotel_detail(request, hotel_id):
    hotel = get_object_or_404(Hotel, pk=hotel_id)
    return render(request, 'csv_upload/hotel_detail.html', {'hotel': hotel})

# from . import lcr_analysis  # Import your lcr_analysis module
from .lcr_analysis import (
    load_csv_data,
    find_lcr,
    find_lcr_for_plot,
    create_lcr_bar_chart,
)

def lcr_analysis(request):
    columns = []
    lcr_results = {}
    unique_countries = []
    unique_operators = []
    chart_image_path = None
    selected_country = request.GET.get('selected_country')
    selected_operator = request.GET.get('selected_operator')

    if request.method == 'GET':
        # print(request.GET)
        csv_file = CSVFile.objects.last()  # Replace with the actual model for your CSV files

        if csv_file:
            csv_file_path = csv_file.file.path
            df = pd.read_csv(csv_file_path)
            columns = df.columns.tolist()
            unique_countries = df['CountryId'].unique().tolist()
            unique_operators = df['OperatorId'].unique().tolist()

            csv_data = load_csv_data(csv_file_path)
            # print(csv_data)

            if selected_country == 'All' and selected_operator == 'All':
                # If both "All" selected, pass the complete CSV data
                lcr_results = csv_data
                print("hsjsj", lcr_results)
            else:
                # Handle the case when specific countries or operators are selected
                if selected_country == 'All':
                    selected_country = None
                if selected_operator == 'All':
                    selected_operator = None

                print("hhhhh", selected_country, selected_operator)
            

                lcr_results = find_lcr(csv_data, country=selected_country, operator=selected_operator)
                print(lcr_results)
                chart_image_path = create_lcr_bar_chart(csv_data, selected_country, selected_operator)

    return render(request, 'csv_upload/lcr_analysis.html', {
        'columns': columns,
        'lcr_results': lcr_results,
        'unique_countries': unique_countries,
        'unique_operators': unique_operators,
        'selected_country': selected_country,
        'selected_operator': selected_operator,
        'chart_image_path': chart_image_path,
    })
