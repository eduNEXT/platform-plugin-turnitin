from openedx_filters import PipelineStep

class CheckTurnitinForPlagiarism(PipelineStep):

    def run_filter(self, context, template_name):
        print("CheckTurnitinForPlagiarism with context: %s" % context)
        return {
            "context": context,
            "template_name": "turnitin/ora.html",
        }
