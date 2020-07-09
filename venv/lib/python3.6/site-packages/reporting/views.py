from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.http import HttpResponse
import reporting
from datetime import date
import csv
import decimal

def report_list(request):
    reports = reporting.all_reports_names()
    return render_to_response('reporting/list.html', {'reports': reports}, 
                              context_instance=RequestContext(request))

def view_report(request, slug):
    for_csv = ''
    count_params = 0
    for key,value in request.REQUEST.iteritems():
        if count_params == 0:
            for_csv = key + '=' + value
        else:
            for_csv = for_csv + '&' + key + '=' + value
        count_params = count_params + 1
    report = reporting.get_report(slug)(request)
    if report.show_details:
        headers = report.get_details_headers()
    else:
        headers = report.get_headers()
    cant_of_group = len(headers) - len(report.aggregate)
    data = {'report': report, 'title':report.verbose_name, 'for_csv':for_csv, 'range':range(cant_of_group),'cant_of_group':cant_of_group +1}
    return render_to_response('reporting/view.html', data, 
                              context_instance=RequestContext(request))
    
def get_csv(request,slug):
    report = reporting.get_report(slug)(request)
    
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=xpot_report_'+ date.today().isoformat() +'.csv'
    
    row_csv = []    
    writer = csv.writer(response)
    # GENERATE HEADERS #
    
    if report.show_details:
        headers = report.get_details_headers()
        row_csv.append(report.get_headers()[0].text)
        for header in headers:
            row_csv.append(str(header))
    else:     
        headers = report.get_headers()
        for header in headers:
            row_csv.append(header.text)
    writer.writerow(row_csv)
    
    for row in report.results:
        
        if report.show_details:
            row_csv = []
            for value in row['details']:
                row_csv = []
                row_csv.append(row['values'][0])
                for final in value:
                    row_csv.append(final)
                writer.writerow(row_csv)
        else:
            row_csv = []
            for value in row['values']:
                row_csv.append(value)
            writer.writerow(row_csv)
    row_csv = []
    if report.show_details:
        headers = report.get_details_headers()
    else:
        headers = report.get_headers()
    cant_of_group = len(headers) - len(report.aggregate)

    row_csv = []
    for i in range(0,cant_of_group):
        row_csv.append('')
    if report.show_details:
        row_csv.append('')
    for title, value in report.get_aggregation():
        row_csv.append(title + ':' + str(value))
    writer.writerow(row_csv)
                    
    return response

def see_plot(request,slug):
    for_csv = slug + '/' + 'csv/?'
    count_params = 0
    for key,value in request.REQUEST.iteritems():
        if count_params == 0:
            if key != 'type_of_plot' and key != 'x_axis' and key != 'y_axis':
                for_csv = for_csv + key + '=' + value
        else:
            if key != 'type_of_plot' and key != 'x_axis' and key != 'y_axis':
                for_csv = for_csv + '&' + key + '=' + value
            
    report = reporting.get_report(slug)(request)
    x_index = 0
    y_index = 0
    data_to_plot = []
    if report.show_details:
        headers = report.get_details_headers()
        x_index = headers.index('x_axis')
        y_index = headers.index('y_axis')
    else:     
        headers = report.get_headers()
        header_tittles =[]
        for header in headers:
            header_tittles.append(header.text)
        x_index = header_tittles.index(request.GET.get('x_axis'))
        y_index = header_tittles.index(request.GET.get('y_axis'))
        for row in report.results:
            new_row = []
            new_row.append(str(row['values'][x_index]))
            if isinstance(row['values'][y_index],decimal.Decimal):
                y_value = float(row['values'][y_index])
            else:
                y_value = row['values'][y_index]
            new_row.append(y_value)
            data_to_plot.append(new_row)
        
    data = {'report': report, 'title':report.verbose_name, 'for_csv':for_csv, 'slug':slug,'data_to_plot':data_to_plot,'type_of_plot':request.GET.get('type_of_plot')}
    return render_to_response('reporting/plot.html', data, 
                              context_instance=RequestContext(request))