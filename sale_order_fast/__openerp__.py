###############################################################################
#
#    Copyright (C) 2001-2014 Micronaet SRL (<http://www.micronaet.it>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

{
    'name': 'Sale order fast line',
    'version': '0.1',
    'category': 'Sales',
    'description': '''  
        Fast insert for order
        ''',
    'author': 'Micronaet S.r.l. - Nicola Riolini',
    'website': 'http://www.micronaet.it',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'sale',
        'sale_stock',
        'mx_sale', # DDT data
        'l10n_it_ddt', # extra partner and doc. data
        'fido_order_check', # fido data
        'mx_discount_scale_order', # for discount operation
        'menuitem_agent', # for agent menu (TODO move in another module?)
        'web_m2x_options', # for options
        'xmlrpc_operation_partner',
        ],
    'init_xml': [],
    'demo': [],
    'data': [
        'security/agent_groups.xml',
        'security/ir.model.access.csv',    
        'fastline_view.xml',
        ],
    'active': False,
    'installable': True,
    'auto_install': False,
    }
