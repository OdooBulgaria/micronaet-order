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
    'name': 'Procurement report wizard',
    'version': '0.1',
    'category': '',
    'description': '''        
        Ex. Procurement report wizard (procurement_report_wizard)
        Add some report used in Company without production
        ''',
    'author': 'Micronaet S.r.l. - Nicola Riolini',
    'website': 'http://www.micronaet.it',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'sale',
        'report_aeroo',
        'production_family', # for famyli filter
        ],
    'init_xml': [],
    'demo': [],
    'data': [
        'order_view.xml',
        'report/order_report.xml',
        'wizard/wizard_order_report.xml',
        ],
    'active': False,
    'installable': True,
    'auto_install': False,
    }