# -*- coding: utf-8 -*-

from openerp import api, fields, models
import logging
import urllib
import urllib2
import xml.etree.ElementTree


_logger = logging.getLogger("# " + __name__)
_logger.setLevel(logging.DEBUG)


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def create_from_ui(self, cr, uid, context):
        res = super(PosOrder, self).create_from_ui(cr, uid, context)
        unlock_product = self.pool['product.product'].search(cr, uid, [('name', '=', 'unlock')])
        for order in context:
            for line in order['data']['lines']:
                pass # TODO
        return res


class UnlockBase(models.Model):
    _inherit = 'unlockbase'

    # add pos category to new mobiles tools
    @api.model
    def create_mobiles_tools(self):
        res = super(UnlockBase, self).create_mobiles_tools()
        self._set_pos_category()
        root = self.env['pos.category'].search([('name', '=', 'Mobile unlock')])
        mobiles_tools = self.env['product.product'].search([('unlockbase_tool_ids', '!=', ''),
                                                            ('pos_categ_id', '==', '')])
        for mobile_tool in mobiles_tools:
            vals = {'name': mobile_tool.categ_id.name, 'parent_id': root}
            new_pos_cat = self.env['pos.category'].create(vals)
            mobile_tool.pos_categ_id = new_pos_cat
            _logger.info('New pos category created and set for %' % mobile_tool.name)
        return res


class UnlockOrder(models.Model):
    _name = 'unlockbase_sales.order'
    #
    # product_id = fields.Many2many('product.product')
    # product_category_id = fields.Many2many('product.category')
    # pos_category_id = fields.Many2many('pos.category')


    def send_action(self, values, cr, uid, context):
        values['Key'] = unlockbase_key
        data = urllib.urlencode(values)
        req = urllib2.Request(unlockbase_url, data)
        response = urllib2.urlopen(req)
        the_page = response.read()
        res = xml.etree.ElementTree.fromstring(the_page)
        return res

    def place_order(self):
        values = {'Key': unlockbase_key,
                  'Action': 'PlaceOrder'}

        data = urllib.urlencode(values)
        req = urllib2.Request(unlockbase_url, data)
        response = urllib2.urlopen(req)
        the_page = response.read()
        print the_page

    def account_info(self):
        values = {'Key': unlockbase_key,
                  'Action': 'AccountInfo'}

        data = urllib.urlencode(values)
        req = urllib2.Request(unlockbase_url, data)
        response = urllib2.urlopen(req)
        the_page = response.read()
        print the_page

        values = {'Key': unlockbase_key,
                  'Action': 'GetMobiles '}

    def get_mobiles (self, cr, uid, context):
        values = {'Action': 'GetMobiles'}
        res = self.send_action(values, cr, uid, context)
        return res