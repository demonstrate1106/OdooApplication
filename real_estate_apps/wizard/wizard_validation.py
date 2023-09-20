from odoo import api, fields, models, _
import csv
import io
import base64
from odoo.exceptions import ValidationError


class WizardValidationEstate(models.TransientModel):
    _name = 'wizard.validation.estate'
    _description = 'Property Validation'

    start_date = fields.Date(string="From: ", required=1)
    end_date = fields.Date(string="To: ", required=True)
    property_buyer = fields.Many2one('res.partner', string="Buyer Name")
    total_property = fields.Integer(string="Total Property", readonly=True)
    total_amount = fields.Float(string="Total Property Amount", readonly=True)
    download_format = fields.Selection([('csv', 'CSV'), ('pdf', 'PDF')], string='Download Format', default='csv')

    def action_validate_property(self):
        domain = [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date)]

        count = self.env['real.estate'].search(domain)
        total = count.mapped('selling_price')
        total_amount = sum(total)
        total_property = len(total)
        self.write({'total_property': total_property, 'total_amount': total_amount})
        return {
            'name': _('Total Property Created Within Given Date'),
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'res_model': 'wizard.validation.estate',
            'target': 'new',
            'effect': {
                'fadeout': 'medium',
                'message': f"{total_property} Property Record Fetched Successfully!!! ",
                'type': 'rainbow_man',
            }
        }

    def action_cancel(self):
        return {
            'effect': {
                'fadeout': 'fast',
                'message': "Closed!!! \n Successfully Closed Wizard 😡",
                'type': 'rainbow_man',
            }
        }

    @api.constrains('end_date')
    def check_end_date(self):
        today = fields.Date.today()
        if self.end_date > today:
            raise ValidationError(_("Input Error in End Date Field \n You can Choose end Date Till Today"))

    def generate_csv_data(self, records):
        csv_data = io.StringIO()
        csv_writer = csv.writer(csv_data)
        header = ['Property Name', 'Price', 'Status', 'date_availability', 'Postcode', 'Bedrooms',
                  'living_area']
        csv_writer.writerow(header)

        for record in records:
            data_row = [record.name, record.selling_price, record.state,
                        record.date_availability,
                        record.postcode, record.bedrooms, record.living_area]
            csv_writer.writerow(data_row)

        return csv_data.getvalue().encode('utf-8')

    def generate_pdf_data(self, records):

        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas

        pdf_data = io.BytesIO()
        c = canvas.Canvas(pdf_data, pagesize=letter)
        c.drawString(100, 750, "Property Name     Price    Status  Date Availability  Living Areas")  # Header

        y = 730  # Initial Y position
        for record in records:
            data_row = f"{record.name} - {record.selling_price} - {record.state} - {record.date_availability} - {record.living_area}"
            c.drawString(100, y, data_row)
            y -= 20  # Adjust the Y position for the next row

        c.save()
        pdf_data.seek(0)

        return pdf_data.getvalue()

    def action_download_data(self):
        domain = [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date)]
        records = self.env['real.estate'].search(domain)

        if self.download_format == 'csv':
            data = self.generate_csv_data(records)
            file_name = 'real_estate_records.csv'
            content_type = 'text/csv'
        elif self.download_format == 'pdf':
            data = self.generate_pdf_data(records)
            file_name = 'real_estate_records.pdf'
            content_type = 'application/pdf'
        else:
            raise ValueError('Invalid download format')

        attachment = self.env['ir.attachment'].create({
            'name': file_name,
            'type': 'binary',
            'datas': base64.b64encode(data),
            'res_model': 'real.estate.download.wizard',
            'res_id': self.id,
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
            'effect': {
                'fadeout': 'medium',
                'message': f" Your {self.download_format} File Downloaded Successfully!",
                'type': 'rainbow_man',
            }
        }


# For Download Filtered Record In Transient model > real_estate module
"""
    def action_download_data(self):
        domain = [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date)]
        records = self.env['real.estate'].search(domain)
        csv_data = io.StringIO()
        csv_writer = csv.writer(csv_data)
        header = ['Property Name', 'Price', 'Status']  # Replace with your actual field names
        csv_writer.writerow(header)

        for record in records:
            data_row = [record.name, record.selling_price, record.state]
            csv_writer.writerow(data_row)
        data_file = csv_data.getvalue().encode('utf-8')
        file_name = 'real_estate_records.csv'
        attachment = self.env['ir.attachment'].create({
            'name': file_name,
            'type': 'binary',
            'datas': base64.b64encode(data_file),
            'res_model': 'real.estate.download.wizard',
            'res_id': self.id,
        })

        # Return an action to download the file
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }
"""
