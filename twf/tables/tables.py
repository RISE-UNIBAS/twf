# pylint: disable=too-few-public-methods
"""This module contains the tables for displaying documents and dictionary entries."""
import django_tables2 as tables
from django.utils.safestring import mark_safe

from twf.models import Document


class DocumentTable(tables.Table):
    """Table for displaying documents."""
    document_id = tables.Column(verbose_name="Document", attrs={"td": {"width": "50%"}})
    pages = tables.Column(verbose_name="Pages")
    options = tables.TemplateColumn(template_name='twf/tables/document_table_options.html',
                                    verbose_name="Options",
                                    attrs={"td": {"width": "10%"}},
                                    orderable=False)

    class Meta:
        """Meta class for the DocumentTable."""
        model = Document
        template_name = "django_tables2/bootstrap.html"  # Using Bootstrap template
        fields = ("document_id", )

    def render_document_id(self, value, record):
        """Renders the document_id column with the title and metadata of the document."""
        html = f"<strong>{value}: {record.title}</strong>"
        for item in record.metadata.items():
            html += f'<br/><span class="small"><u>{item[0]}</u>: {item[1]}</span>'

        return mark_safe(html)

    def render_pages(self, record):
        """Renders the pages column with the number of pages and the number of ignored pages."""
        html = '<div class="container">'
        html += '  <div class="row">'
        html += self.get_col("ID", 3)
        html += self.get_col("Page", 3)
        html += self.get_col("Blocks", 3)
        html += self.get_col("Tags", 3)
        html += '  </div>'

        for page in record.pages.all().order_by('tk_page_number'):
            html += '<div class="row">'
            html += self.get_col(page.tk_page_id, 3, ignored=page.is_ignored)
            html += self.get_col(page.tk_page_number, 3, ignored=page.is_ignored)
            html += self.get_col(len(page.parsed_data["elements"])\
                                     if page.parsed_data else 0, 3, ignored=page.is_ignored)
            html += self.get_col(f"{page.tags.count()} / {page.tags.filter(dictionary_entry=None).count()}",
                                 3, ignored=page.is_ignored)
            html += '</div>'
        html += '</div>'

        return mark_safe(html)

    @staticmethod
    def get_col(value, size, ignored=False):
        """Returns a column div with the given value and size. If ignored is True, the value is crossed out."""
        html = f'<div class="col-{size} border small">'
        if ignored:
            html += f'<s class="text-muted" style="text-decoration-style: wavy">{value}</s>'
        else:
            html += f'{value}'
        html += '</div>'

        return html
