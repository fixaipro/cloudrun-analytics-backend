import importlib, re

def dispatch(report_type, file_url):
    slug = re.sub(r'\W+', '_', report_type.strip().lower()).strip('_')
    module_path = f"analytics_modules.{slug}"
    try:
        mod = importlib.import_module(module_path)
    except ImportError:
        raise ValueError(f"Unknown report type: {report_type}")
    if not hasattr(mod, 'run'):
        raise ValueError(f"Module {module_path} missing run()")
    return mod.run(file_url)
