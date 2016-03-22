# -*- coding: utf-8 -*-
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
import os
import sys
import logging
import openerp
import openerp.netsvc as netsvc
import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv, expression, orm
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp import SUPERUSER_ID, api
from openerp import tools
from openerp.tools.translate import _
from openerp.tools.float_utils import float_round as round
from openerp.tools import (DEFAULT_SERVER_DATE_FORMAT, 
    DEFAULT_SERVER_DATETIME_FORMAT, 
    DATETIME_FORMATS_MAP, 
    float_compare)


_logger = logging.getLogger(__name__)

class SaleOrderFastline(orm.Model):
    """ Model name: sale order fastline
    """    
    _name = 'sale.order.fastline'
    _description = 'Fast line'
    
    _columns = {
        'order_id': fields.many2one(
            'sale.order', 'Order Reference', ondelete='cascade'),
        'product_id': fields.many2one(
            'product.product', 'Product', domain=[('sale_ok', '=', True)], 
            required=True),
        'price_unit': fields.float(
            'Unit Price', digits_compute=dp.get_precision('Product Price')),
        'product_uom_qty': fields.float(
            'Quantity', digits_compute= dp.get_precision('Product UoS'), 
            required=True),
        #'discount': fields.float('Discount (%)', 
        #    digits_compute=dp.get_precision('Discount')),
        #'price_subtotal': fields.function(
        #    _amount_line, string='Subtotal', 
        #    digits_compute= dp.get_precision('Account')),
        #'tax_id': fields.many2many(
        #    'account.tax', 'sale_order_tax', 'order_line_id', 'tax_id', 
        #    'Taxes'),
        #'product_uom': fields.many2one(
        #    'product.uom', 'Unit of Measure ', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        #'product_uos_qty': fields.float(
        #    'Quantity (UoS)', digits_compute=dp.get_precision('Product UoS'), 
        #    ),
        #'product_uos': fields.many2one('product.uom', 'Product UoS'),
        }

class SaleOrder(orm.Model):
    """ Model name: StockDdt
    """    
    _inherit = 'sale.order'
    
    def show_fastorder(self, cr, uid, ids, context=None):
        '''
        '''
        return self.write(cr, uid, ids, {'fast_order': True}, context=context)
        
    def create_real_line(self, cr, uid, ids, context=None):
        ''' Create real line from fast one's
        '''
        assert len(ids) == 1, 'Only one order a time'
        sol_pool = self.pool.get('sale.order.line')
        fastline_pool = self.pool.get('sale.order.fastline')
        
        
        order_proxy = self.browse(cr, uid, ids, context=context)[0]
        multi_discount_rates = order_proxy.partner_id.discount_rates
        # TODO discount_value
        fastline_ids = []
        for fastline in order_proxy.fastline_ids:
            # -----------------------------------------------------------------
            #               Compose data for sale order line
            # -----------------------------------------------------------------            
            # Get onchange data on product:
            data = sol_pool.product_id_change_with_wh(
                cr, uid, False,                
                order_proxy.pricelist_id.id,
                fastline.product_id.id,
                qty=fastline.product_uom_qty,
                uom=fastline.product_id.uom_id.id, 
                qty_uos=fastline.product_uom_qty, 
                uos=fastline.product_id.uos_id.id, 
                name=fastline.product_id.name, 
                partner_id=order_proxy.partner_id.id,
                lang=context.get('lang', 'it_IT'), 
                update_tax=True, 
                date_order=order_proxy.date_order, 
                packaging=False, 
                fiscal_position=order_proxy.fiscal_position.id, 
                flag=False, 
                warehouse_id=order_proxy.warehouse_id.id, 
                context=context,
                ).get('value', {})

            # Tax bug:
            data['tax_id'] = [(6, 0, data['tax_id'])]
            
            # Discount block:
            data.update(sol_pool.on_change_multi_discount(
                cr, uid, False, multi_discount_rates, context=context,
                ).get('value', {}))
            data['multi_discount_rates'] = multi_discount_rates
            
            # Fasline data:
            data.update({
                'order_id': order_proxy.id,
                'product_id': fastline.product_id.id,
                'product_uom_qty': fastline.product_uom_qty,
                #'product_uom_id': fastline.product_id.id,
                })
                
            # Force price:
            if fastline.price_unit:
                data['price_unit'] = fastline.price_unit
                
            sol_pool.create(cr, uid, data, context=context)
            fast_list.append(fastline.id)
            
        # Delete fast line:
        fastline_pool.unlink(cr, uid, fastline_ids, context=context)    
        
        # Remove fast order 
        self.write(cr, uid, ids, {
            'fast_order': False,
            }, context=context)
        return True
        
    _columns = {
        'fastline_ids': fields.one2many(
            'sale.order.fastline', 'order_id', 'Fast line'), 
        'fast_order': fields.boolean('Fast order'),    
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
