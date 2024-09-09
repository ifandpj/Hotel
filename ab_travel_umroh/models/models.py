# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class TravelPackage(models.Model):
	_name = 'travel.package'
	_description = 'Travel Package'

	name = fields.Char(string='Nama Paket', compute='_computed_name_get', store=True)
	ref = fields.Char(string='Kode Travel', readonly=True, default='-', tracking=True)
	tanggal_berangkat = fields.Date(string='Tanggal Berangkat', readonly=True, required=True, states={'draft': [('readonly', False)]})
	tanggal_kembali = fields.Date(string='Tanggal Kembali', readonly=True, required=True, states={'draft': [('readonly', False)]})
	product_id = fields.Many2one('product.product', string='Sale', readonly=True, required=True, states={'draft': [('readonly', False)]})
	product_package_id = fields.Many2one('mrp.bom', string='Package', readonly=True, required=True, states={'draft': [('readonly', False)]})
	sale_order_id = fields.Many2one('sale.order', string='Sale Order')
	quota = fields.Integer(string='Quota', readonly=True, required=True, states={'draft': [('readonly', False)]})
	remaining_quota = fields.Integer(string='Remaining Quota', compute='_compute_remaining_quota', readonly=True, store=True)
	quota_progress = fields.Float(string='Quota Progress', readonly=True, store=True)
	state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'), ('done', 'Done')], string='Status', readonly=True, default='draft')
	hotel_line = fields.One2many('hotel.line', 'package_id', readonly=True, string='Hotel', states={'draft': [('readonly', False)]})
	airline_line = fields.One2many('airline.line', 'package_id', readonly=True, string='Airline', states={'draft': [('readonly', False)]})
	schedule_line = fields.One2many('schedule.line', 'package_id', readonly=True, string='Schedule', states={'draft': [('readonly', False)]})
	manifest_line = fields.One2many('manifest.line', 'package_id', string='Manifest', readonly=True, store=True, states={'draft': [('readonly', False)]})
	hpp_line = fields.One2many('hpp.line', 'package_id', string='HPP', store=True, states={'confirm': [('readonly', True)], 'done': [('readonly', True)]})

	total_cost = fields.Float(string='Total Cost', compute='_compute_total_cost', store=True)

	@api.model
	def create(self, vals):
		vals['ref'] = self.env['ir.sequence'].next_by_code('travel.package')
		return super(TravelPackage, self).create(vals)

	@api.depends('ref', 'product_id')
	def _computed_name_get(self):
		for record in self:
			name = record.ref + ' - ' + record.product_id.name
			record.name = name
		# return result

	def action_confirm(self):
		self.write({'state': 'confirm'})

	def action_cancel(self):
		self.write({'state': 'draft'})

	def action_close(self):
		self.write({'state': 'done'})

	# VARIASI 1
	# def action_update_manifest(self):
	# 	num = 0
	# 	travel_package_cancel_order = self.env['sale.order'].search([('travel_package_id', '=', self.id), ('state', 'in', ('draft', 'cancel'))])
	# 	travel_package_done_order = self.env['sale.order'].search([('travel_package_id', '=', self.id), ('state', 'in', ('sale', 'done'))])
	# 	# self.manifest_line.unlink()

	# 	if travel_package_cancel_order:
	# 		for travel_package in travel_package_cancel_order:
	# 			for manifest in travel_package.manifest_line:
	# 				manifest.write({
	# 					'package_id': None,
	# 				})

	# 	for travel_package in travel_package_done_order:
	# 		for manifest in travel_package.manifest_line:
	# 			manifest.write({
	# 				'package_id': self.id,
	# 			})
	# 			num += 1

	# 	self.remaining_quota = self.quota - num
	# 	self.quota_progress = (num / self.quota) * 100
	# VARIASI 2
	def action_update_manifest(self):
		num = 0
		new_list = []
		travel_package_done_order = self.env['sale.order'].search([('travel_package_id', '=', self.id), ('state', 'in', ('sale', 'done'))])

		self.manifest_line = [(5, 0, 0)]

		for travel_package in travel_package_done_order:
			for manifest in travel_package.manifest_line:
				new_list.append((0, 0, {
					'package_id': self.id,
					'partner_id': manifest.partner_id.id,
					'age': manifest.age,
					'room_type': manifest.room_type,
					'mahrom_id': manifest.mahrom_id.id,
					'users_id': manifest.users_id.id,
				}))
				num += 1
		self.manifest_line = new_list
		self.remaining_quota = self.quota - num
		self.quota_progress = (num / self.quota) * 100

	def action_cetak_manifest(self):
		return self.env.ref('ab_travel_umroh.report_travel_package_manifest_action').report_action(self)

	@api.onchange('product_package_id')
	def _onchange_product_id(self):
		hpp_lines = []
		total = 0
		self.hpp_line = [(5, 0, 0)]
		for record in self.product_package_id.bom_line_ids:
				subtotal = record.product_qty * record.product_id.standard_price
				hpp_lines.append((0, 0, {
						'barang': record.product_id.name,
						'qty': record.product_qty,
						'unit': record.product_uom_id.name,
						'unit_price': record.product_id.standard_price,
						'subtotal': subtotal,
				}))
				total += subtotal

		self.hpp_line = hpp_lines

	@api.depends('hpp_line.subtotal')
	def _compute_total_cost(self):
		for record in self:
			subtotal = sum(line.subtotal for line in record.hpp_line)
			record.total_cost = subtotal

	@api.depends('quota')
	def _compute_remaining_quota(self):
		# print('INI TOTAL MANIFEST', len(self.manifest_line))
		if len(self.manifest_line) > 0:
			if self.quota < len(self.manifest_line):
				raise ValidationError('Terdapat %s peserta yang telah terdaftar pada %s. Anda tidak dapat mengurangi jumlah quota!' % (len(self.manifest_line), self.name))
			else:
				self.remaining_quota = self.quota - len(self.manifest_line)
				self.quota_progress = (len(self.manifest_line) / self.quota) * 100
		else:
			self.remaining_quota = self.quota
			self.quota_progress = 0

	@api.constrains('quota')
	def _check_quota(self):
		if self.quota <= 0:
			raise ValidationError('Quota tidak boleh sama dengan 0!')

class Hotels(models.Model):
	_name = 'hotel.line'
	_description = 'Hotel Line'

	package_id = fields.Many2one('travel.package', string='Package')
	partner_id = fields.Many2one('res.partner', string='Hotel', domain=[('hotel', '=', True)])
	check_in = fields.Date(string='Check In', required=True)
	check_out = fields.Date(string='Check Out', required=True)
	destinasi = fields.Char(string='Destinasi', related='partner_id.city', readonly=True)

class Airlines(models.Model):
	_name = 'airline.line'
	_description = 'Airline Line'

	package_id = fields.Many2one('travel.package', string='Package')
	partner_id = fields.Many2one('res.partner', string='Airline', domain=[('airline', '=', True)])
	tanggal_berangkat = fields.Date(string='Tanggal Berangkat', required=True)
	kota_asal = fields.Char(string='Kota Asal', required=True)
	kota_tujuan = fields.Char(string='Kota Tujuan', required=True)

class Schedules(models.Model):
	_name = 'schedule.line'
	_description = 'Schedule Line'

	package_id = fields.Many2one('travel.package', string='Package')
	nama_kegiatan = fields.Char(string='Nama Kegiatan', required=True)
	tanggal_kegiatan = fields.Date(string='Tanggal Kegiatan', required=True)

class Manifest(models.Model):
	_name = 'manifest.line'
	_description = 'Manifest Line'

	package_id = fields.Many2one('travel.package', string='Package')
	sale_order_id = fields.Many2one('sale.order', string='Manifest', ondelete='cascade') # seharusnya di ganti menjadi sale_order_id

	partner_id = fields.Many2one('res.partner', string='Nama Jamaah', required=True)
	title = fields.Many2one(related='partner_id.title', string='Title')
	jenis_kelamin = fields.Selection(readonly=True, string='Jenis Kelamin', related='partner_id.jenis_kelamin', selection=[('Laki - Laki', 'Laki - Laki'), ('Perempuan', 'Perempuan')])
	room_type = fields.Selection(string='Tipe Kamar', selection=[('Double', 'Double'), ('Triple', 'Triple'), ('Quad', 'Quad')], default='Quad')
	tanggal_lahir = fields.Date(readonly=True, string='Tanggal Lahir', related='partner_id.tanggal_lahir')
	no_ktp = fields.Char(readonly=True, string='No. KTP', related='partner_id.no_ktp')
	mahrom_id = fields.Many2one('res.partner', string='Mahrom')
	age = fields.Integer(string='Umur', compute='_compute_age', store=True, readonly=True)
	tempat_lahir = fields.Char(readonly=True, string='Tempat Lahir', related='partner_id.tempat_lahir')

	no_passpor = fields.Char(readonly=True, string='No. Passpor', related='partner_id.no_passpor')
	tanggal_berlaku = fields.Date(readonly=True, string='Tanggal Berlaku', related='partner_id.tanggal_berlaku')
	imigrasi = fields.Char(readonly=True, string='Imigrasi', related='partner_id.imigrasi')
	nama_passpor = fields.Char(readonly=True, string='Nama Passpor', related='partner_id.nama_passpor')
	tanggal_expired = fields.Date(readonly=True, string='Tanggal Expired', related='partner_id.tanggal_expired')
	notes = fields.Text(string='Notes')

	scan_passpor = fields.Image(string="Scan Passpor", related='partner_id.scan_passpor')
	scan_ktp = fields.Image(string="Scan KTP", related='partner_id.scan_ktp')
	scan_buku_nikah = fields.Image(string="Scan Buku Nikah", related='partner_id.scan_buku_nikah')
	scan_kartu_keluarga = fields.Image(string="Scan Kartu Keluarga", related='partner_id.scan_kartu_keluarga')

	users_id = fields.Many2one('res.users', string='Users', default=lambda self: self.env.user)

	@api.depends('tanggal_lahir')
	def _compute_age(self):
		for record in self:
			record.age = 0
			if record.tanggal_lahir:
				record.age = (fields.Date.today() - record.tanggal_lahir).days / 365

class Hpp(models.Model):
	_name = 'hpp.line'
	_description = 'HPP Line'

	package_id = fields.Many2one('travel.package', string='Package')
	barang = fields.Char(string='Barang', required=True)
	qty = fields.Integer(string='Quantity')
	unit = fields.Char(string='Unit(s)')
	unit_price = fields.Float(string='Unit Price')
	subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal', store=True)

	@api.depends('qty', 'unit_price')
	def _compute_subtotal(self):
		for record in self:
			record.subtotal = record.qty * record.unit_price

class AccountMove(models.Model):
	_inherit = 'account.move'

	def action_cetak_invoices(self):
		return self.env.ref('ab_travel_umroh.report_invoice_action').report_action(self)

	def get_payment(self):
		bill = [
			('ref', 'ilike', self.name),
		]
		return self.env['account.payment'].search(bill)

class Partner(models.Model):
	_inherit = 'res.partner'

	no_ktp = fields.Char(string="No KTP")
	nama_ayah = fields.Char(string="Nama Ayah")
	pekerjaan_ayah = fields.Char(string="Pekerjaan Ayah")
	tempat_lahir = fields.Char(string="Tempat Lahir")
	pendidikan = fields.Selection(string="Pendidikan", selection=[('SD', 'SD'), ('SMP', 'SMP'), ('SMA', 'SMA'), ('Sarjana', 'S1'), ('Pascasarjana', 'S2'), ('Doktor', 'S3')])
	status_hubungan = fields.Selection(string="Status Hubungan", selection=[('Menikah', 'Married'), ('Lajang', 'Single'), ('Cerai', 'Divorced')])
	jenis_kelamin = fields.Selection(string="Jenis Kelamin", selection=[('Laki - Laki', 'Laki - Laki'), ('Perempuan', 'Perempuan')])
	nama_ibu = fields.Char(string="Nama Ibu")
	pekerjaan_ibu = fields.Char(string="Pekerjaan Ibu")
	tanggal_lahir = fields.Date(string="Tanggal Lahir")
	golongan_darah = fields.Selection(string="Golongan Darah", selection=[('A', 'A'), ('B', 'B'), ('AB', 'AB'), ('O', 'O')])
	ukuran_baju = fields.Selection(string="Ukuran Baju", selection=[('XS', 'XS'), ('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL'), ('XXL', 'XXL'), ('XXXL', 'XXXL'), ('4XL', '4XL')])
	no_passpor = fields.Char(string="No Passpor")
	tanggal_berlaku = fields.Date(string="Tanggal Berlaku")
	imigrasi = fields.Char(string="Imigrasi")
	nama_passpor = fields.Char(string="Nama Passpor")
	tanggal_expired = fields.Date(string="Tanggal Expired")
	scan_passpor = fields.Image(string="Scan Passpor")
	scan_ktp = fields.Image(string="Scan KTP")
	scan_buku_nikah = fields.Image(string="Scan Buku Nikah")
	scan_kartu_keluarga = fields.Image(string="Scan Kartu Keluarga")
	hotel = fields.Boolean(string="Hotel")
	airline = fields.Boolean(string="Airline")

class SaleOrder(models.Model):
	_inherit = 'sale.order'

	travel_package_id = fields.Many2one('travel.package', string='Paket Perjalanan', domain=[('state', '=', 'confirm')])
	manifest_line = fields.One2many('manifest.line', 'sale_order_id', string='Manifest', states={'sale': [('readonly', True)], 'done': [('readonly', True)]})

	@api.onchange('travel_package_id')
	def _onchange_travel_package_id(self):
		if self.travel_package_id:
			if self.travel_package_id.remaining_quota == 0:
				raise ValidationError('Paket Perjalanan Ini Sudah Penuh. Silahkan Pilih Paket Perjalanan Lainnya.. :D')
			else:
				new_order_lines = []
				self.order_line = [(5, 0, 0)]
				for package in self.travel_package_id:
						new_order_lines.append((0, 0, {
								'product_id': package.product_id.id,
								'product_uom_qty': 1,
						}))

				self.order_line = new_order_lines

	@api.constrains('manifest_line')
	def _check_manifest_line(self):
		if len(self.manifest_line) == 0:
			raise ValidationError('Harap Isi Data Manifest Terlebih Dahulu.. :D')
		else:
			if self.travel_package_id:
				if len(self.manifest_line) > self.travel_package_id.remaining_quota:
					raise ValidationError('Jumlah Peserta Melebihi Kuota Paket Perjalanan. Silahkan Hapus Peserta Yang Tidak Diperlukan.. :D')
				else:
					pass

class StockPicking(models.Model):
	_inherit = 'stock.picking'

	def action_print_delivery(self):
		return self.env.ref('ab_travel_umroh.report_delivery_order_action').report_action(self)