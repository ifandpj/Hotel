from odoo import models, fields

class HotelMember(models.Model):
    _inherit = 'res.partner'

    transaksi_line = fields.One2many('transaksi.hotel', 'member_id', string='Transaksi Booking')
