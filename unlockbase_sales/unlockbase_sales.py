# -*- coding: utf-8 -*-

from openerp import api, fields, models
import logging
import urllib
import urllib2
import xml.etree.ElementTree
from openerp.exceptions import UserError
from openerp.tools.translate import _

_logger = logging.getLogger("# " + __name__)
_logger.setLevel(logging.DEBUG)


class UnlockBase(models.Model):
    _inherit = 'unlockbase'

    # add pos category to new mobiles tools
    @api.model
    def create_mobiles_tools(self):
        res = super(UnlockBase, self).create_mobiles_tools()
        root = self.env['pos.category'].search([('name', '=', 'Mobile unlock')])
        mobiles_tools_cats = self.env['product.category'].search([('brand_id', '!=', '')])
        for cat in mobiles_tools_cats:
            mobiles_tools = self.env['product.product'].search([('unlock_service', '=', True),
                                                                    ('categ_id', '=', cat.id),
                                                                    ('pos_categ_id', '=', False)])
            old_pos_cat = self.env['pos.category'].search([('name', '=', cat.name)])
            for mobile_tool in mobiles_tools:
                if len(old_pos_cat) == 0:
                    vals = {'name': mobile_tool.categ_id.name, 'parent_id': root.id}
                    new_pos_cat = self.env['pos.category'].create(vals)
                    _logger.info('New pos category created %s' % mobile_tool.categ_id.name)
                    mobile_tool.pos_categ_id = new_pos_cat.id
                elif len(old_pos_cat) == 1:
                    mobile_tool.pos_categ_id = old_pos_cat.id
                    _logger.info('Mobile tool updated %s' % mobile_tool.name)
                self.env.cr.commit()
        return res


class PosOrder(models.Model):
    _inherit = 'pos.order'

    unlockbase_order_id = fields.Char(string='Unlock order id', default='None', readonly=True)
    unlockbase_order_state = fields.Selection([('draft', 'Draft'), ('placed', 'Placed'), ('validated', 'Validated')], string='Unlock state',  default='draft', readonly=True)
    IMEI = fields.Char(string='IMEI', default='None', required=True)
    email = fields.Char(string='email', default='None', required=True)
    unlockbase_network = fields.Char(string='network', default='None')
    unlockbase_mobile = fields.Char(string='mobile', default='None')
    unlockbase_provider = fields.Char(string='provider', default='None')
    unlockbase_pin = fields.Char(string='pin', default='None')
    unlockbase_kbh = fields.Char(string='kbh', default='None')
    unlockbase_mep = fields.Char(string='mep', default='None')
    unlockbase_prd = fields.Char(string='prd', default='None')
    unlockbase_sn = fields.Char(string='sn', default='None')
    unlockbase_secro = fields.Char(string='secro', default='None')
    unlockbase_reference = fields.Char(string='reference', default='None')
    unlockbase_servicetag = fields.Char(string='servicetag', default='None')
    unlockbase_icloudemail = fields.Char(string='icloudemail', default='None')
    unlockbase_icloudphone = fields.Char(string='icloudphone', default='None')
    unlockbase_icloududid = fields.Char(string='icloududid', default='None')
    unlockbase_type = fields.Char(string='type', default='None')
    unlockbase_locks = fields.Char(string='locks', default='None')

    @api.model
    def create_from_ui(self, context):
        res = super(PosOrder, self).create_from_ui(context)
        for order_id in res:
            self.set_fields(order_id)
        return res

    @api.model
    def set_fields(self, order_id):
        order = self.env['pos.order'].browse(order_id)
        unlock_tool = order.lines[0].product_id.unlockbase_tool_ids[0]
        order.unlockbase_network = unlock_tool.requires_network
        order.unlockbase_mobile = unlock_tool.requires_mobile
        order.unlockbase_provider = unlock_tool.requires_provider
        order.unlockbase_pin = unlock_tool.requires_pin
        order.unlockbase_kbh = unlock_tool.requires_kbh
        order.unlockbase_mep = unlock_tool.requires_mep
        order.unlockbase_prd = unlock_tool.requires_prd
        order.unlockbase_sn = unlock_tool.requires_sn
        order.unlockbase_secro = unlock_tool.requires_secro
        order.unlockbase_reference = unlock_tool.requires_reference
        order.unlockbase_servicetag = unlock_tool.requires_servicetag
        order.unlockbase_icloudemail = unlock_tool.requires_icloudemail
        order.unlockbase_icloudphone = unlock_tool.requires_icloudphone
        order.unlockbase_icloududid = unlock_tool.requires_icloududid
        order.unlockbase_type = unlock_tool.requires_type
        order.unlockbase_locks = unlock_tool.requires_locks

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

    @api.model
    def action_place_order(self, ids):
        order = self.env['pos.order'].browse(ids)
        unlock_tool = order.lines[0].product_id.unlockbase_tool_ids[0]
        vals = {'IMEI': order.IMEI, 'Email': order.email}
        if unlock_tool.requires_network != 'None':
            if lame(order.unlockbase_network):
                raise UserError(_('Please set unlock network.'))
            else:
                vals['Network'] = order.unlockbase_network
        if unlock_tool.requires_mobile != 'None':
            if lame(order.unlockbase_mobile):
                raise UserError(_('Please set unlock mobile id.'))
            else:
                vals['Mobile'] = order.unlockbase_network
        if unlock_tool.requires_provider != 'None':
            if lame(order.unlockbase_provider):
                raise UserError(_('Please set unlock provider.'))
            else:
                vals['Mobile'] = order.unlockbase_provider


        # TODO other fields
        res = self.unlockbase_place_order(vals)
        try:
            suc = res.find('Success').text
            _logger.info(suc)
            order.unlockbase_order_id = res.find('ID').text
        except:
            raise UserError(_('Bad order'))  # TODO
        order.unlockbase_order_state = 'placed'


def nice(s):
    if s in ['', 'None', None, False]:
        return False
    return True


def lame(s):
    if s in ['', 'None', None, False]:
        return True
    return False