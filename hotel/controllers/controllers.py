from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)

class HotelRoomController(http.Controller):
   

    @http.route('/hotel/rooms', type='http', auth='public', methods=['GET'], csrf=False)
    def get_rooms(self):
        try:
            rooms = request.env['base.hotel'].sudo().search_read([], [
                'name', 'lantai', 'panjang', 'lebar', 'luas', 'state', 'harga_malam', 'fasilitas_ids', 'transaksi_line'
            ])

           
            data = []
            for room in rooms:
                room_data = {
                    'name': room['name'],
                    'lantai': room['lantai'],
                    'panjang': room['panjang'],
                    'lebar': room['lebar'],
                    'luas': room['panjang'] * room['lebar'],
                    'state': room['state'],
                    'harga_malam': room['harga_malam'],
                  
                }

               
                facility_ids = room.get('fasilitas_ids', [])
                if facility_ids:
                    facilities = request.env['fasilitas.hotel'].sudo().search_read([('id', 'in', facility_ids)], ['name'])
                    room_data['fasilitas'] = [facility['name'] for facility in facilities]

              
                transaction_ids = room.get('transaction_ids', [])
                if transaction_ids:
                    transactions = request.env['transaksi.hotel'].sudo().search_read([('id', 'in', transaction_ids)], 
                                                                                ['partner_id', 'start_date', 'end_date', 'state'])
                    room_data['booking_transactions'] = [{
                        'member_id': transaction['partner_id'][1] if transaction['partner_id'] else '',
                        'start_date': transaction['start_date'].strftime('%Y-%m-%d') if transaction['start_date'] else None,
                        'end_date': transaction['end_date'].strftime('%Y-%m-%d') if transaction['end_date'] else None,
                        'status': transaction['state']
                    } for transaction in transactions]

                data.append(room_data)

            
            return request.make_response(json.dumps(data), [('Content-Type', 'application/json')])

        except Exception as e:
            return request.make_response(json.dumps({'error': str(e)}), [('Content-Type', 'application/json')])
        
        
        
        
    
    @http.route('/hotel/rooms/create', type='json', auth='public', methods=['POST'], csrf=False)
    def create_room(self, **kwargs):
        try:
         
            data = request.jsonrequest

         
            if not data:
                return {'error': "No data received. Please check the JSON payload."}

           
            required_fields = ['name', 'lantai', 'panjang', 'lebar',  'state', 'harga_malam', 'fasilitas_ids']
            for field in required_fields:
                if field not in data:
                    return {'error': f"Field '{field}' is required."}

           
            new_room = request.env['base.hotel'].sudo().create({
                'name': data.get('name'),
                'lantai': data.get('lantai'),
                'panjang': data.get('panjang'),
                'lebar': data.get('lebar'),
                'state': data.get('state'),
                'harga_malam': data.get('harga_malam'),
                'fasilitas_ids': [(6, 0, data.get('fasilitas_ids', []))]  # Menggunakan command 6 untuk memperbarui many2many relasi
            })

           
         
            return {'success': True, 'room_id': new_room.id}

        except Exception as e:
         
            return {'error': str(e)}
        
        
        
    @http.route('/hotel/rooms/update/<int:kamar_id>', type='json', auth='public', methods=['PUT', 'PATCH'], csrf=False)
    def update_room(self, kamar_id):
        try:
           
            data = request.jsonrequest

            room = request.env['base.hotel'].sudo().search([('id', '=', kamar_id)], limit=1)

           
            if room:
               
                room.write(data)
                return {'success': True, 'message': f"Room with ID {kamar_id} updated successfully."}
            else:
                return {'error': f"Room with ID {kamar_id} not found."}

        except Exception as e:
           
            return {'error': str(e)}

        
        
        
    @http.route('/hotel/rooms/delete/<int:kamar_id>', type='http', auth='public', methods=['DELETE'], csrf=False)
    def delete_room(self, kamar_id, **kwargs):
        try:
          
            room = request.env['base.hotel'].sudo().search([('id', '=', kamar_id)], limit=1)

            
            if room:
                room_name = room.name
                room.unlink()
                return request.make_response(json.dumps({'success': True, 'message': f"Room with ID {kamar_id} deleted successfully."}), headers={'Content-Type': 'application/json'})
            else:
                return request.make_response(json.dumps({'error': f"Room with ID {kamar_id} not found."}), headers={'Content-Type': 'application/json'})

        except Exception as e:
            return request.make_response(json.dumps({'error': str(e)}), headers={'Content-Type': 'application/json'})
