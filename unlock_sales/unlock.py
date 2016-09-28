# -*- coding: utf-8 -*-

from openerp import api, fields, models
import urllib
import urllib2

class PosOrder(models.Model):
    _inherit = 'pos.order'

    def create_from_ui(self, cr, uid, context):
        res = super(PosOrder, self).create_from_ui(cr, uid, context)
        unlock_product = self.env['product.product'].search([('name', '=', 'unlock')])
        for order in context:
            for line in order['data']['lines']:
                if line['product_id'] == unlock_product.id:
                    self.place_order(order.id)
                    pass
        return res

    def place_order(self):
