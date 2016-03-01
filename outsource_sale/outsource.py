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
import pickle
import tempfile
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

class ResCompany(orm.Model):
    """ Model name: ResCompany
    """    
    _inherit = 'res.company'
    
    _columns = {
        'outsourced_partner_id': fields.many2one(
            'res.partner', 'Outsourced partner', 
            help='Partner linked as company ref. (used in order header)', 
            required=False),     
        }    

class SaleOrder(orm.Model):
    """ Model name: Sale order
    """    
    _inherit = 'sale.order'

    # -------------------------------------------------------------------------
    #                             REMOTE PROCEDURE: 
    # -------------------------------------------------------------------------
    def erpeek_stock_order_in(self, cr, uid, pickle_file):
        ''' Read temp file and get data
        '''
        pickle_f = open(pickle_file, 'r')
        order_dict = pickle.load(pickle_f)
        pickle_f.close()
        return order_dict

    def create_order_outsource(self, cr, uid, pickle_file, context=None):
        ''' XMLRPC procedure for import order in current company 
            @return esit        
        '''
        sol_pool = self.pool.get('sale.order.line')
        # Read dictionary passed:
        order_dict = self.erpeek_stock_order_in(cr, uid, pickle_file)
        
        # ---------------------------------------------------------------------
        #                              HEADER
        # ---------------------------------------------------------------------
        # Create order if not present:
        name = order_dict['header'].name
        order_ids = self.search(cr, uid, [], context=context)
        if order_ids:
            return _('Order jet present! Delete and reimport if not started!')
        
        partner_id = 0
        data = self.onchange_partner_id(cr, uid, False, partner_id, 
            context=context).get('value', {})        
        data.update({
            'partner_id': partner_id, 
            'linked': True, # as outsource            
            })
        order_id = self.create(cr, uid, data, context=context)

        # ---------------------------------------------------------------------
        #                                LINE
        # ---------------------------------------------------------------------
        for line in order_dict['line']:
            # TODO onchange event?
            sol_pool.create(cr, uid, {
                
                }, context=context)

        try:
            os.remove(res)
        except:
            pass # do nothing

        return False # no error    
        
    # -------------------------------------------------------------------------
    #                             MASTER PROCEDURE: 
    # -------------------------------------------------------------------------
    def erpeek_stock_order_out(self, cr, uid, data):
        ''' Function called by Erpeek with dict passed by pickle file
        '''
        pickle_f = tempfile.NamedTemporaryFile(delete=False)
        pickle.dump(dicts, pickle_f)
        res = f.name 
        pickle_f.close()
        return res

    def create_order_outsource(self, cr, uid, ids, context=None):
        ''' Create order in other company
        '''
        assert len(ids) == 1, 'Call only for once'
        
        order_dict = {}
        for order in self.browse(cr, uid, ids, context=context):
            order_dict['header'] = {
                'name': order.name,
                'date_order': order.date_order,
                'date_deadline': order.date_deadline,
                'date_confirm': order.date_confirm,
                'client_order_ref': order.client_order_ref,
                'note': _(
                    'Imported order\n Partner: %s [%s]\nDestination:\n' + \
                    'Total: %s [Taxed: %s]\nCustomer ref.:'
                    ) % (
                        order.partner_id.name,
                        order.partner_id.sql_customer_code,
                        order.destination_partner_id.name \
                            if order.destination_partner_id else '/', 
                        order.amount_untaxed,
                        order.amount_total,               
                        order.client_order_ref,             
                    )                
                }
            order_dict['line'] = []
            for line in order.order_line:
                if not line.outsource:
                    continue
                order_dict['line'].append({
                    line.product_id.default_code,
                    line.product_uom_qty,
                    line.date_deadline,                    
                    })    
                    
        # Write pickle file:        
        pickle_file = self.erpeek_stock_order_out(
            cr, uid, order_dict, context=context) 
        
        # Call XML RPC import procedure:
        #esit = create_order_outsource(cr, uid, pickle_file)
        # if esit # write outsource
        
        return True
        
    _columns = {
        'outsource': fields.boolean('Outsource order', 
            help='This order will be outsourced'),
        'linked': fields.boolean('Linked order', 
            help='This order has an order in other company'),
        }
    

class SaleOrderLine(orm.Model):
    """ Model name: Sale order line
    """
    
    _inherit = 'sale.order.line'
    
    def nothing(self, cr, uid, ids, context=None):
        return True
    
    _columns = {
        'outsource': fields.related(
            'product_id', 'outsource', 
            type='boolean', string='Outsource', store=False), 
        }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
