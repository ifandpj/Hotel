from odoo import models, fields

class FasilitasHotel(models.Model):
    _name = 'fasilitas.hotel'
    _description = 'Fasilitas Hotel'

    name = fields.Char(string='Nama', required=True)
    kode = fields.Char(string='Code', required=True)
