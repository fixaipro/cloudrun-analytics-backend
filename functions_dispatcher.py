from analytics_modules import all_analysis_dispatch

def dispatch(report_type, file_url):
    if report_type not in all_analysis_dispatch.mapping:
        raise ValueError(f"Unknown report type: {report_type}")
    # call the corresponding function
    return all_analysis_dispatch.mapping[report_type](file_url)
