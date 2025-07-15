from analytics_modules.all_analysis_scripts import analysis_a, analysis_b

def dispatch(report_type, file_url):
    if report_type == 'A':
        return analysis_a(file_url)
    elif report_type == 'B':
        return analysis_b(file_url)
    else:
        raise ValueError(f"Unknown report type: {report_type}")
