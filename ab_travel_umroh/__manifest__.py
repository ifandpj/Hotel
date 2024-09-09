# -*- coding: utf-8 -*-
{
    'name': "AB Travel Umroh",

    'summary': """
        Modul Travel Umroh untuk tugas akhir""",

    'description': """
        Modul ini berfungsi untuk mempraktekan technical documentation pada website resmi odoo.com. Sebagian hal yang akan dipelajari adalah :
        - ORM
        - Berbagai View
        - Report
        - Wizard
        - Dll
    """,

    'author': "PT. Ismata Nusantara Abadi",
    'website': "https://www.ismata.co.id",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product', 'mrp', 'sale', 'stock', 'report_xlsx'],

    # always loaded
    'data': [
		'report/report_stock_picking_delivery.xml',
		'report/report_account_move_invoice.xml',
		'report/custom_report_paper.xml',
		'report/report_action.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/sequence_data.xml',
		'views/masterdata_views.xml',
		'views/travel_package_views.xml',
		'views/menuitem_views.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,
}
