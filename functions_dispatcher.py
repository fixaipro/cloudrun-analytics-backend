import importlib
import re

def dispatch(report_type, file_url):
    """
    Dynamically import analytics_modules.<slug> and call its `run` function.
    report_type can be anything; we convert it to a Python-safe slug:
      e.g. "Scenario Planner" → "scenario_planner"
    """
    # 1) turn the label into a slug
    slug = re.sub(r'\W+', '_', report_type.strip().lower()).strip('_')
    module_path = f"analytics_modules.{slug}"

    # 2) dynamically import that module
    try:
        mod = importlib.import_module(module_path)
    except ImportError:
        raise ValueError(f"Unknown report type: {report_type}")

    # 3) call its `run(file_url)` function
    if not hasattr(mod, 'run'):
        raise ValueError(f"Module {module_path} has no run() function")
    return mod.run(file_url)
