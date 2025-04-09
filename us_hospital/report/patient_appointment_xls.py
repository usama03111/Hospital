

from odoo import models
import base64
import io


class PatientAppointmentXlsx(models.AbstractModel):
    _name = 'report.us_hospital.report_patient_appointment_xls'
    _inherit = 'report.report_xlsx.abstract'


    def generate_xlsx_report(self, workbook, data, patients):
        bold = workbook.add_format({'bold': True})
        sheet = workbook.add_worksheet("Appointments")
        format_1 = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': 'yellow' ,})
        row = 3
        col = 3
        sheet.write(row, col, "Reference", format_1)
        sheet.write(row, col + 1, "Patient Name", format_1)
        sheet.set_column('D:D', 18)
        sheet.set_column('E:E', 20)
        for appointment in data["appointments"]:
            row +=1
            sheet.write(row, col, appointment["serial_no"] , )
            sheet.write(row, col + 1, appointment["patient_id"][1] ,)

        #     row = 3
        #     col = 1
        #
        #     sheet.merge_range(row, col, row, col + 1, "ID Card", format_1)
        #     row += 1
        #     if obj.image:
        #         patient_image = io.BytesIO(base64.b64decode(obj.image))
        #         sheet.insert_image(row, col, 'image.png', {'image_data': patient_image, 'x_scale': 0.3, 'y_scale': 0.3})
        #         row += 8
        #
        #     sheet.write(row, col, "Name", bold)
        #     sheet.write(row, col + 1, obj.name, )
        #     row += 1
        #     sheet.write(row, col, "Age", bold)
        #     sheet.write(row, col + 1, obj.age, )
        #     row += 1
        #     sheet.write(row, col, "reference", bold)
        #     sheet.write(row, col + 1, obj.reference, )
        #
        #     row +=3
        #     sheet.merge_range(row , col , row+3 , col+3 , "usama wazir" , format_1 )
