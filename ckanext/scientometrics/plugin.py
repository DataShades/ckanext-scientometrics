import ckan.plugins.toolkit as tk
from ckan import plugins as p
from ckan.common import CKANConfig


@tk.blanket.helpers
@tk.blanket.actions
@tk.blanket.auth_functions
@tk.blanket.config_declarations
@tk.blanket.cli
class ScientometricsPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)
    # p.implements(p.IScientometrics)

    # IConfigurer

    def update_config(self, config_: CKANConfig):
        tk.add_template_directory(config_, "templates")
        tk.add_public_directory(config_, "public")
        tk.add_resource("assets", "scientometrics")

    # IScientometrics

    # def get_extractors(self):
    #     return {
    #         "google_scholar": GoogleScholarMetricsExtractor,
    #     }
