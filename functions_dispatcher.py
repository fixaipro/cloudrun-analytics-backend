import importlib
import re

def dispatch(report_type, file_url):
    """
    Dynamically load analytics_modules.<slug> and call its run(file_url).
    slug is derived from the human-friendly report_type:
      - lowercase
      - non-word chars -> underscores
      - strip leading/trailing underscores
    """
    slug = re.sub(r'\W+', '_', report_type.strip().lower()).strip('_')
    module_path = f"analytics_modules.{slug}"
    try:
        mod = importlib.import_module(module_path)
    except ImportError:
        raise ValueError(f"Unknown report type: {report_type}")
    if not hasattr(mod, 'run'):
        raise ValueError(f"Module {module_path} has no run(file_url) function")
    return mod.run(file_url)
