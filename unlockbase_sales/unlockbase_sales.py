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

    @api.model
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
        root = self.env['pos.category'].search([('name', '=', 'Mobile unlock')])
        mobiles_tools = self.env['product.product'].search([('unlock_service', '=', True)])
        for mobile_tool in mobiles_tools:
            old_pos_cat = self.env['pos.category'].search([('name', '=', mobile_tool.categ_id.name)])
            if len(old_pos_cat) == 0:
                vals = {'name': mobile_tool.categ_id.name, 'parent_id': root.id}
                new_pos_cat = self.env['pos.category'].create(vals)
                _logger.info('New pos category created %s' % mobile_tool.categ_id.name)
                mobile_tool.pos_categ_id = new_pos_cat
            elif len(old_pos_cat) == 1:
                mobile_tool.pos_categ_id = old_pos_cat
                _logger.info('Mobile tool updated %s' % old_pos_cat.name)

        return res


class PosOrder(models.Model):
    _inherit = 'pos.order'

    unlockbase_order_state = fields.Selection([('draft', 'Draft'), ('placed', 'Placed'), ('validated', 'Validated')])
    unlockbase_network = fields.Char()
    unlockbase_mobile = fields.Char()
    unlockbase_provider = fields.Char()
    unlockbase_pin = fields.Char()
    unlockbase_kbh = fields.Char()
    unlockbase_mep = fields.Char()
    unlockbase_prd = fields.Char()
    unlockbase_sn = fields.Char()
    unlockbase_secro = fields.Char()
    unlockbase_reference = fields.Char()
    unlockbase_servicetag = fields.Char()
    unlockbase_icloudemail = fields.Char()
    unlockbase_icloudphone = fields.Char()
    unlockbase_icloududid = fields.Char()
    unlockbase_type = fields.Char()
    unlockbase_locks = fields.Char()

    def unlockbase_place_order(self):
        return self.unlockbase_send_action({'Action': 'PlaceOrder'})

    def unlockbase_account_info(self):
        return self.unlockbase_send_action({'Action': 'AccountInfo'})

    @api.model
    def unlockbase_send_action(self, values):
        unlockbase_url = self.env['ir.config_parameter'].sudo().get_param('unlockbase.url')
        values['Key'] = self.env['ir.config_parameter'].sudo().get_param('unlockbase.key')
        data = urllib.urlencode(values)
        req = urllib2.Request(unlockbase_url, data)
        response = urllib2.urlopen(req)
        the_page = response.read()
        if 'Unauthorized IP address' in the_page:
            _logger.error(
                'Unauthorized IP address ERROR. Please check security configuration in unlockbase.com settings.')
            return False
        res = xml.etree.ElementTree.fromstring(the_page)
        return res
