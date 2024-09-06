from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date

class TransaksiHotel(models.Model):
    _name = 'transaksi.hotel'
    _description = 'Transaksi Hotel'
    _rec_name = 'member_id'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('finish', 'Finish'),
        ('cancel', 'Cancel')], string='Status', default='draft')
    member_id = fields.Many2one('res.partner', string='Member')
    room_id = fields.Many2one('base.hotel', string='Kamar')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    duration = fields.Integer(string='Duration', compute='_compute_duration', store=True)
    note = fields.Text(string='Note')
    total_active = fields.Integer(
        string='Total Active Transactions',
        compute='_compute_total_active',
        store=True
    )
    
    total_finish = fields.Integer(
        string='Total Finished Transactions',
        compute='_compute_total_finish',
        store=True
    )
    
    total_cancel = fields.Integer(
        string='Total Cancelled Transactions',
        compute='_compute_total_cancel',
        store=True
    )

    @api.depends('state')
    def _compute_total_active(self):
        for record in self:
            record.total_active = self.search_count([('state', '=', 'active')])

    @api.depends('state')
    def _compute_total_finish(self):
        for record in self:
            record.total_finish = self.search_count([('state', '=', 'finished')])

    @api.depends('state')
    def _compute_total_cancel(self):
        for record in self:
            record.total_cancel = self.search_count([('state', '=', 'cancelled')])

    @api.depends('start_date', 'end_date')
    def _compute_duration(self):
        for record in self:
            if record.start_date and record.end_date:
                record.duration = (record.end_date - record.start_date).days + 1

    def action_confirm(self):
        self.state = 'active'
        self.room_id.check_availability()
        

    def action_cancel(self):
        self.state = 'cancel'
        self.room_id.check_availability()

    def _check_end_date(self):
        # Automatic status change to finish when end date is reached
        today = fields.Date.today()
        for transaction in self:
            if transaction.end_date and transaction.end_date < today and transaction.status == 'active':
                transaction.status = 'finish'
                
    @api.constrains('room_id', 'start_date', 'end_date')
    def check_room_availability(self):
        for record in self:
            # Cek apakah ada transaksi aktif yang bertabrakan dengan transaksi yang dibuat
            overlapping_transactions = self.env['transaksi.hotel'].search([
                ('id', '!=', record.id),
                ('room_id', '=', record.room_id.id),
                ('state', '=', 'active'),
                ('start_date', '<=', record.end_date),
                ('end_date', '>=', record.start_date),
            ])
            if overlapping_transactions:
                raise ValidationError(
                    _('Room "%s" is already booked from %s to %s. Please select another date or room.') %
                    (record.room_id.name, overlapping_transactions[0].start_date, overlapping_transactions[0].end_date)
                )
                
                
                
    @api.model
    def auto_update_transaction_status(self):
        """ Automatically update the transaction status from 'active' to 'finish' 
        when the end_date is passed. """
        today = date.today()
        transactions = self.search([('state', '=', 'active'), ('end_date', '<', today)])
        for transaction in transactions:
            transaction.state = 'finish'
            transaction.room_id.check_availability()