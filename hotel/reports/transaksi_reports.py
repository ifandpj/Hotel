from odoo import api, models

class HotelTransactionReport(models.AbstractModel):
    _name = 'report.hotel.trasnaksi_hotel_invoice'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['transkasi.hotel'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'transaksi.hote',
            'docs': docs,
        }