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

    ub_codes = fields.Char(string='Unlock codes')
    ub_order_id = fields.Char(string='Unlock order id', default='None', readonly=True)
    ub_order_state = fields.Selection([('draft', 'Draft'), ('placed', 'Placed'), ('validated', 'Validated'), ('canceled', 'Canceled')], string='Unlock state',  default='draft', readonly=True)
    IMEI = fields.Char(string='IMEI', default='None', required=True)
    email = fields.Char(string='email', default='None', required=True)
    ub_network = fields.Char(string='network', default='None')
    ub_mobile = fields.Char(string='mobile', default='None')
    ub_provider = fields.Char(string='provider', default='None')
    ub_pin = fields.Char(string='pin', default='None')
    ub_kbh = fields.Char(string='kbh', default='None')
    ub_mep = fields.Char(string='mep', default='None')
    ub_prd = fields.Char(string='prd', default='None')
    ub_sn = fields.Char(string='sn', default='None')
    ub_secro = fields.Char(string='secro', default='None')
    ub_reference = fields.Char(string='reference', default='None')
    ub_servicetag = fields.Char(string='servicetag', default='None')
    ub_icloudemail = fields.Char(string='icloudemail', default='None')
    ub_icloudphone = fields.Char(string='icloudphone', default='None')
    ub_icloududid = fields.Char(string='icloududid', default='None')
    ub_type = fields.Char(string='type', default='None')
    ub_locks = fields.Char(string='locks', default='None')

    @api.model
    def create_from_ui(self, context):
        res = super(PosOrder, self).create_from_ui(context)
        for order_id in res:
            self.set_fields(order_id)
        return res

    @api.model
    def set_fields(self, order_id):
        order = self.env['pos.order'].browse(order_id)
        tool = order.lines[0].product_id.unlockbase_tool_ids[0]
        order.ub_network = tool.req_network
        order.ub_mobile = tool.req_mobile
        order.ub_provider = tool.req_provider
        order.ub_pin = tool.req_pin
        order.ub_kbh = tool.req_kbh
        order.ub_mep = tool.req_mep
        order.ub_prd = tool.req_prd
        order.ub_sn = tool.req_sn
        order.ub_secro = tool.req_secro
        order.ub_reference = tool.req_reference
        order.ub_servicetag = tool.req_servicetag
        order.ub_icloudemail = tool.req_icloudemail
        order.ub_icloudphone = tool.req_icloudphone
        order.ub_icloududid = tool.req_icloududid
        order.ub_type = tool.req_type
        order.ub_locks = tool.req_locks

    def check_fields(self, order, tool):
        vals = {'IMEI': order.IMEI, 'Email': order.email}

        if nice(tool.req_network):
            if lame(order.ub_network):
                raise UserError(_('Please set unlock network.'))
            else:
                vals['Network'] = order.ub_network

        if nice(tool.req_mobile):
            if lame(order.ub_mobile):
                raise UserError(_('Please set unlock mobile id.'))
            else:
                vals['Mobile'] = order.ub_network

        if nice(tool.req_provider):
            if lame(order.ub_provider):
                raise UserError(_('Please set unlock provider.'))
            else:
                vals['Provider'] = order.ub_provider

        if nice(tool.req_pin):
            if lame(order.ub_pin):
                raise UserError(_('Please set unlock pin.'))
            else:
                vals['PIN'] = order.ub_pin

        if nice(tool.req_kbh):
            if lame(order.ub_kbh):
                raise UserError(_('Please set unlock KBH.'))
            else:
                vals['KBH'] = order.ub_kbh

        if nice(tool.req_mep):
            if lame(order.ub_mep):
                raise UserError(_('Please set unlock MEP.'))
            else:
                vals['MEP'] = order.ub_mep

        if nice(tool.req_prd):
            if lame(order.ub_prd):
                raise UserError(_('Please set unlock PRD.'))
            else:
                vals['PRD'] = order.ub_prd

        if nice(tool.req_type):
            if lame(order.ub_type):
                raise UserError(_('Please set unlock type.'))
            else:
                vals['Type'] = order.ub_type

        if nice(tool.req_locks):
            if lame(order.ub_locks):
                raise UserError(_('Please set unlock locks.'))
            else:
                vals['Locks'] = order.ub_locks

        if nice(tool.req_sn):
            if lame(order.ub_sn):
                raise UserError(_('Please set unlock SN.'))
            else:
                vals['SN'] = order.ub_sn

        if nice(tool.req_secro):
            if lame(order.ub_secro):
                raise UserError(_('Please set unlock SECRO.'))
            else:
                vals['SecRO'] = order.ub_secro

        # Values below returned after 'Action': 'GetTools' but did not described in API v3
        #
        # if nice(tool.req_reference):
        #     if lame(order.ub_reference):
        #         raise UserError(_('Please set unlock reference.'))
        #     else:
        #         vals['Mobile'] = order.ub_reference
        #
        # if nice(tool.req_servicetag):
        #     if lame(order.ub_servicetag):
        #         raise UserError(_('Please set unlock service tag.'))
        #     else:
        #         vals['Mobile'] = order.ub_servicetag
        #
        # if nice(tool.req_icloudemail):
        #     if lame(order.ub_icloudemail):
        #         raise UserError(_('Please set unlock ub_icloude mail.'))
        #     else:
        #         vals['Mobile'] = order.ub_icloudemail
        #
        # if nice(tool.req_icloudphone):
        #     if lame(order.ub_icloudphone):
        #         raise UserError(_('Please set unlock icloud phone.'))
        #     else:
        #         vals['Mobile'] = order.ub_icloudphone
        #
        # if nice(tool.req_icloududid):
        #     if lame(order.ub_icloududid):
        #         raise UserError(_('Please set unlock icloud udid.'))
        #     else:
        #         vals['Mobile'] = order.ub_icloududid

        return vals

    # ACTIONS #
    @api.model
    def action_place_order(self, ids):
        order = self.env['pos.order'].browse(ids)
        tool = order.lines[0].product_id.unlockbase_tool_ids[0]
        vals = self.check_fields(order, tool)
        res = self.unlockbase_place_order(vals)
        if res.find('Error') == 0:
            raise UserError(res.find('Error').text)
        try:
            suc = res.find('Success').text
            _logger.info(suc)
            order.ub_order_id = res.find('ID').text
        except:
            raise UserError('Bad order')
        order.ub_order_state = 'placed'
        if res.find('Codes') != 0:
            order.ub_order_id = res.find('Codes').text  # For instant tools

    @api.model
    def action_cancel_order(self, ids):
        order = self.env['pos.order'].browse(ids)
        vals = {'ID': order.ub_order_id}
        res = self.unlockbase_cancel_order(vals)
        if res.find('Error') != 0:
            raise UserError('Order can not be canceled. %s' % res.find('Error').text)
        if res.find('Pending') != 0:
            raise UserError('Order could not be cancelled now and a cancellation request has been sent. %s' % res.find('Pending').text)
        if res.find('Success') != 0:
            order.ub_order_state = 'canceled'
            _logger.info('Order has been canceled. %s' % res.find('Success').text)

    @api.model  # TODO
    def action_verify_order(self, ids):
        order = self.env['pos.order'].browse(ids)
        vals = {'ID': order.ub_order_id}
        res = self.unlockbase_verify_order(vals)
        if res.find('Error') != 0:
            raise UserError('Order can not be canceled. %s' % res.find('Error').text)
        if res.find('Pending') != 0:
            raise UserError('Order could not be cancelled now and a cancellation request has been sent. %s' % res.find('Pending').text)
        if res.find('Success') != 0:
            order.ub_order_state = 'canceled'
            _logger.info('Order has been canceled. %s' % res.find('Success').text)

    @api.model  # TODO
    def action_retry_order(self, ids):
        order = self.env['pos.order'].browse(ids)
        vals = {'ID': order.ub_order_id}
        res = self.unlockbase_retry_order(vals)
        if res.find('Error') != 0:
            raise UserError('Order can not be canceled. %s' % res.find('Error').text)
        if res.find('Pending') != 0:
            raise UserError('Order could not be cancelled now and a cancellation request has been sent. %s' % res.find('Pending').text)
        if res.find('Success') != 0:
            order.ub_order_state = 'canceled'
            _logger.info('Order has been canceled. %s' % res.find('Success').text)

    # API v3 unlockbase #
    def unlockbase_verify_order(self, vals):
        vals['Action'] = 'VerifyOrder'
        return self.unlockbase_send_action(vals)

    def unlockbase_retry_order(self, vals):
        vals['Action'] = 'RetryOrder'
        return self.unlockbase_send_action(vals)

    def unlockbase_place_order(self, vals):
        vals['Action'] = 'PlaceOrder'
        return self.unlockbase_send_action(vals)

    def unlockbase_cancel_order(self, vals):
        vals['Action'] = 'CancelOrder'
        return self.unlockbase_send_action(vals)

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
            _logger.error('Unauthorized IP address ERROR. Please check security configuration in unlockbase.com settings.')
            return False
        res = xml.etree.ElementTree.fromstring(the_page)
        return res


def nice(s):
    if s in ['', 'None', None, False]:
        return False
    return True


def lame(s):
    if s in ['', 'None', None, False]:
        return True
    return False