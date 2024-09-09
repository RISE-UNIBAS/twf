from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.generic import FormView

from twf.forms.export_forms import ExportDataForm
from twf.views.views_project import TWFProjectView
from twf.tasks.export_tasks import export_data_task


class TWFExportDataView(FormView, TWFProjectView):
    template_name = 'twf/project/export.html'  # Path to your export template
    page_title = 'Export Data'
    form_class = ExportDataForm
    success_url = reverse_lazy('export_data')  # You can change this to the desired success URL

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.get_project()
        return kwargs

    def form_valid(self, form):
        project = self.get_project()

        export_type = form.cleaned_data['export_type']
        export_format = form.cleaned_data['export_format']
        schema = form.cleaned_data['schema']

        # Start the export process using Celery
        task = export_data_task.delay(project.id, export_type, export_format, schema)

        # Return the task ID for progress tracking (assuming this view is called via AJAX)
        return JsonResponse({'status': 'success', 'task_id': task.id})

    def form_invalid(self, form):
        # If the form is invalid, return the errors
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
