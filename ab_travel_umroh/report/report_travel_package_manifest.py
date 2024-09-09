from odoo import api, fields, models

class ManifestXlsx(models.AbstractModel):
    _name = 'report.ab_travel_umroh.report_manifest'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, obj):
        sheet = workbook.add_worksheet('Manifest %s' % obj.name)
        text_top_style = workbook.add_format({'font_size': 12, 'bold': True, 'font_color' : 'black', 'valign': 'vcenter', 'text_wrap': True, 'border': 3, 'align': 'center'})
        text_header_style = workbook.add_format({'font_size': 12, 'bold': True ,'font_color' : 'white', 'bg_color': 'blue', 'valign': 'vcenter', 'text_wrap': True, 'align': 'center', 'border': 1})
        text_style = workbook.add_format({'font_size': 12, 'valign': 'vcenter', 'text_wrap': True, 'align': 'center', 'border': 3})
        number_style = workbook.add_format({'num_format': '#,##0', 'font_size': 12, 'align': 'right', 'valign': 'vcenter', 'text_wrap': True})

        sheet.write(1,2, 'MANIFEST', text_top_style)
        sheet.write(1,3, obj.ref, text_top_style)

        header = ['NO', 'TITLE', 'GENDER', 'FULLNAME', 'TEMPAT LAHIR', 'TANGGAL LAHIR', 'NO. PASSPOR', 'PASSPOR ISSUED', 'PASSPOR EXPIRED', 'IMIGRASI', 'MAHROM', 'USIA', 'NIK', 'ORDER', 'ROOM TYPE', 'ROOM LEADER', 'NO. ROOM', 'ALAMAT']
        header_airline = ['NO', 'AIRLINE', 'DEPARTURE DATE', 'DEPARTURE CITY', 'ARRIVAL CITY']

        no_list = []
        title = []
        gender = []
        fullname = []
        tempat_lahir = []
        tanggal_lahir = []
        no_passpor = []
        passpor_issued = []
        passpor_expired = []
        imigrasi = []
        mahrom = []
        usia = []
        nik = []
        order = []
        room_type = []
        room_leader = []
        no_room = []
        alamat = []

        no = 1
        row = 5
        skip = 0
        for x in obj.manifest_line:
            no_list.append(no)
            title.append(x.partner_id.title.name)
            gender.append(x.jenis_kelamin)
            fullname.append(x.partner_id.name)
            tempat_lahir.append(x.tempat_lahir)
            tanggal_lahir.append(x.tanggal_lahir.strftime('%d %B, %Y'))
            no_passpor.append(x.no_passpor)
            passpor_issued.append(x.tanggal_berlaku.strftime('%d %B, %Y'))
            passpor_expired.append(x.tanggal_expired.strftime('%d %B, %Y'))
            imigrasi.append(x.imigrasi)
            mahrom.append(x.mahrom_id.name if x.mahrom_id else '-')
            usia.append(x.age)
            nik.append(x.no_ktp)
            order.append(x.sale_order_id.name)
            room_type.append(x.room_type)
            room_leader.append('-')
            no_room.append('-')
            alamat.append(x.partner_id.city)
            no+=1
            skip+=1

        print('ini alamat', alamat)

        no_list_airline = []
        airline = []
        departure_date = []
        departure_city = []
        arrival_city = []

        no_airline = 1
        for x in obj.airline_line:
            no_list_airline.append(no_airline)
            airline.append(x.partner_id.name)
            departure_date.append(x.tanggal_berangkat.strftime('%d %B, %Y'))
            departure_city.append(x.kota_asal)
            arrival_city.append(x.kota_tujuan)
            no_airline+=1

        print('ini airline', airline)

        sheet.write_row(4, 0, header, text_header_style)
        sheet.write_row(4+skip+3, 2, header_airline, text_header_style)

        sheet.set_column(1, 1, 15)
        sheet.set_column(2, 2, 25)
        sheet.set_column(3, 3, 40)
        sheet.set_column(4, 4, 27)
        sheet.set_column(5, 5, 27)
        sheet.set_column(6, 6, 25)
        sheet.set_column(7, 7, 28)
        sheet.set_column(8, 8, 28)
        sheet.set_column(9, 9, 28)
        sheet.set_column(10, 10, 40)
        sheet.set_column(12, 12, 30)
        sheet.set_column(13, 13, 28)
        sheet.set_column(14, 14, 28)
        sheet.set_column(15, 15, 29)
        sheet.set_column(16, 16, 29)
        sheet.set_column(17, 17, 40)

        sheet.write_column(row, 0, no_list, text_style)
        sheet.write_column(row, 1, title, text_style)
        sheet.write_column(row, 2, gender, text_style)
        sheet.write_column(row, 3, fullname, text_style)
        sheet.write_column(row, 4, tempat_lahir, text_style)
        sheet.write_column(row, 5, tanggal_lahir, text_style)
        sheet.write_column(row, 6, no_passpor, text_style)
        sheet.write_column(row, 7, passpor_issued, text_style)
        sheet.write_column(row, 8, passpor_expired, text_style)
        sheet.write_column(row, 9, imigrasi, text_style)
        sheet.write_column(row, 10, mahrom, text_style)
        sheet.write_column(row, 11, usia, text_style)
        sheet.write_column(row, 12, nik, text_style)
        sheet.write_column(row, 13, order, text_style)
        sheet.write_column(row, 14, room_type, text_style)
        sheet.write_column(row, 15, room_leader, text_style)
        sheet.write_column(row, 16, no_room, text_style)
        sheet.write_column(row, 17, alamat, text_style)

        sheet.write_column(row+skip+3, 2, no_list_airline, text_style)
        sheet.write_column(row+skip+3, 3, airline, text_style)
        sheet.write_column(row+skip+3, 4, departure_date, text_style)
        sheet.write_column(row+skip+3, 5, departure_city, text_style)
        sheet.write_column(row+skip+3, 6, arrival_city, text_style)