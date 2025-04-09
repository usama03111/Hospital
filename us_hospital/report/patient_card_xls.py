from odoo import models
import base64
import io


class PatientCardXlsx(models.AbstractModel):
    _name = 'report.us_hospital.report_patient_id_card_xls'
    _inherit = 'report.report_xlsx.abstract'

    ##--> if you want to print on a single sheet all the patient data

    # def generate_xlsx_report(self, workbook, data, patients):
    #     sheet = workbook.add_worksheet('Patient Data'[:31])
    #     bold = workbook.add_format({'bold': True})
    #     format_1 = workbook.add_format({'bold':True , 'align':'center' , 'bg_color': 'yellow'})
    #     row=3
    #     col=1
    #     sheet.set_column('B:C',15)
    #     for obj in patients:
    #
    #         sheet.merge_range(row , col , row , col+1 , "ID Card", format_1)
    #         row +=1
    #         if obj.image:
    #             patient_image = io.BytesIO(base64.b64decode(obj.image))
    #             sheet.insert_image(row , col ,'image.png' , {'image_data':patient_image,'x_scale':0.3,'y_scale':0.3 })
    #             row+=8
    #
    #
    #         sheet.write(row, col, "Name", bold)
    #         sheet.write(row, col+1, obj.name,)
    #         row+=1
    #         sheet.write(row , col , "Age" ,bold)
    #         sheet.write(row , col+1 , obj.age ,)
    #         row += 1
    #         sheet.write(row , col , "reference",bold)
    #         sheet.write(row , col+1 , obj.reference,)
    #
    #         row +=2

##---> if you want to print all the patient data on every single sheet

    def generate_xlsx_report(self, workbook, data, patients):
        bold = workbook.add_format({'bold': True})
        format_1 = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': 'yellow' ,})

        for obj in patients:
            sheet = workbook.add_worksheet(obj.name[:31])
            sheet.set_column('B:C', 15)
            row = 3
            col = 1

            sheet.merge_range(row, col, row, col + 1, "ID Card", format_1)
            row += 1
            if obj.image:
                patient_image = io.BytesIO(base64.b64decode(obj.image))
                sheet.insert_image(row, col, 'image.png', {'image_data': patient_image, 'x_scale': 0.3, 'y_scale': 0.3})
                row += 8

            sheet.write(row, col, "Name", bold)
            sheet.write(row, col + 1, obj.name, )
            row += 1
            sheet.write(row, col, "Age", bold)
            sheet.write(row, col + 1, obj.age, )
            row += 1
            sheet.write(row, col, "reference", bold)
            sheet.write(row, col + 1, obj.reference, )

            row +=3
            sheet.merge_range(row , col , row+3 , col+3 , "usama wazir" , format_1 )
