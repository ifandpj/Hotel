from odoo import models, fields, api

class BaseHotel(models.Model):
    _name = 'base.hotel'
    _description = 'Hotel Room'
  

    name = fields.Char(string='Nama Kamar', required=True)
    lantai = fields.Integer(string='Lantai')
    panjang = fields.Float(string='Panjang Kamar (m)')
    lebar = fields.Float(string='Lebar Kamar (m)')
    luas = fields.Float(string='Luas Kamar (m²)', compute='_compute_luas')
    state = fields.Selection([('available', 'Available'), ('booked', 'Booked')], string='Status', default='available')
    harga_malam = fields.Float(string='Price per Malam')
    fasilitas_ids = fields.Many2many('fasilitas.hotel', string='Fasilitas Kamar')
    transaksi_line = fields.One2many('transaksi.hotel', 'room_id', string='Transaksi Booking')

    @api.depends('panjang', 'lebar')
    def _compute_luas(self):
        for record in self:
            record.luas = record.panjang * record.lebar

    def check_availability(self):
        
        today = fields.Date.today()
        for room in self:
            if room.transaksi_line.filtered(lambda t: t.start_date <= today <= t.end_date and t.state == 'active'):
                room.state = 'booked'
            else:
                room.state = 'available'
