# -*- coding: utf-8 -*-

from openerp import api, fields, models
import threading
import openerp
import logging
import urllib
import urllib2
import xml.etree.ElementTree
import base64
import re
import string
from bs4 import BeautifulSoup as bs


_logger = logging.getLogger("# " + __name__)
_logger.setLevel(logging.DEBUG)

unlockbase_url = 'http://www.unlockbase.com/xml/api/v3'  # TODO place in ir config parameter
unlockbase_key = '(C8C7-4533-06AE-3151)'  # TODO place in ir config parameter


class ProductProduct(models.Model):
    _inherit = 'product.product'

    unlock_mobile_id = fields.Char(string='unlock_mobile_id')
    unlockbase_tool_id = fields.Many2many('unlockbase.tool')


class ProductCategory(models.Model):
    _inherit = 'product.category'

    brand_id = fields.Char(string='Mobile brand')


class UnlockBase(models.Model):
    _name = 'unlockbase'

    active = fields.Boolean()

    @api.model
    def action_load_from_unlockbase(self):
        _logger.info('Loading of unlockbase.com mobiles database started')
        all_good = True
        while all_good:
            all_good = self.create_brands_and_mobiles()  # create, brand, mobile and mobile tools category
            # all_good = self.create_tools()   # create tools with bound mobiles to it
            # all_good = self.create_mobiles_tools()  # for each mobile we create available unlock tools
            _logger.info('Data from unlockbase.com loaded successfully')
        _logger.info('Errors occurred while unlockbase.com data loading')


    @api.model
    def create_brands_and_mobiles(self):
        res = self.get_all_data()
        if res is False:
            return False
        mobiles_cat = self.env['product.category'].search([('name', '=', 'Mobiles')], limit=1)
        all_brands = self.env['product.category'].search([('parent_id', '=', mobiles_cat.id)])
        all_brands_names = [r.name for r in all_brands]
        categ_to_bind = 1  # TEMP
        for brand in res.findall('Brand'):
            brand_id = brand.find('ID').text
            brand_name = make_tech_name(brand.find('Name').text)
            all_brand_mobiles = [r.mobile_tech_name for r in self.env['product.product'].search([('mobile_brand', '=', brand_name)])]
            old_brand = self.env['product.category'].search([('name', '=', brand_name)])
            if brand_name not in all_brands_names:
                # TEMP
                vals = {'brand_id': brand_id, 'name': brand_name, 'parent_id': mobiles_cat.id}
                # Create brand
                new_cat = self.env['product.category'].create(vals)
                categ_to_bind = new_cat.id
                _logger.info('New brand created: %s' % new_cat.name)
            else:
                if not old_brand.brand_id or old_brand.brand_id != brand_id:
                    old_brand.brand_id = brand_id
                    categ_to_bind = old_brand.id
            for mobile in brand.findall('Mobile'):
                unlock_mobile_id = mobile.find('ID').text
                mobile_name = make_tech_name(mobile.find('Name').text)
                mobile_photo = mobile.find('Photo').text.replace('https', 'http')
                if mobile_name not in all_brand_mobiles:
                    resp = urllib.urlopen(mobile_photo)
                    photo = None
                    # if resp.code == 200:
                    #     photo = base64.b64encode(resp.read())
                    vals = {'unlock_mobile_id': unlock_mobile_id,
                            'name': mobile_name,
                            'image': photo,
                            'categ_id': categ_to_bind,
                            'sale_ok': False}
                    # Create mobile
                    new_mobile = self.env['product.product'].create(vals)
                    _logger.info('New mobile created: %s %s' % (brand_name, new_mobile.name))
                    # Create category for unlock tools for this phone
                    vals = {'brand_id': brand_id, 'name': mobile_name, 'parent_id': old_brand.id}
                    unlock_cat = self.env['product.category'].create(vals)
                    _logger.info('New unlock mobile tools category created: %s' % unlock_cat.name)
                    # TEMP
                    # return True
                else:
                    old_mobile = self.env['product.product'].search([('mobile_tech_name', '=', mobile_name)])
                    if not old_mobile.unlock_mobile_id or old_mobile.unlock_mobile_id != unlock_mobile_id:
                        old_mobile.unlock_mobile_id = unlock_mobile_id
                        _logger.info('Old mobile updated: %s' % old_mobile.name)
                self.write({'active': True})
        return True

    @api.model
    def create_tools(self):
        tools_list = self.get_tools()
        all_mobiles_tools = []
        for group in tools_list.findall('Group'):
            for tool in group.findall('Tool'):
                vals = dict()
                vals['name'] = tool.find('Name').text
                vals['group_id'] = group.find('ID').text
                vals['group_name'] = group.find('Name').text
                vals['tool_id'] = tool.find('ID').text
                vals['tool_name'] = tool.find('Name').text
                vals['credits'] = tool.find('Credits').text
                vals['type'] = tool.find('Type').text
                vals['sms'] = tool.find('SMS').text
                vals['message'] = tool.find('Message').text
                vals['delivery_min'] = tool.find('Delivery.Min').text
                vals['delivery_max'] = tool.find('Delivery.Max').text
                vals['delivery_unit'] = tool.find('Delivery.Unit').text
                vals['requires_network'] = tool.find('Requires.Network').text
                vals['requires_mobile'] = tool.find('Requires.Mobile').text
                vals['requires_provider'] = tool.find('Requires.Provider').text
                vals['requires_pin'] = tool.find('Requires.PIN').text
                vals['requires_kbh'] = tool.find('Requires.KBH').text
                vals['requires_mep'] = tool.find('Requires.MEP').text
                vals['requires_prd'] = tool.find('Requires.PRD').text
                vals['requires_sn'] = tool.find('Requires.SN').text
                vals['requires_secro'] = tool.find('Requires.SecRO').text
                vals['requires_reference'] = tool.find('Requires.Reference').text
                vals['requires_servicetag'] = tool.find('Requires.ServiceTag').text
                vals['requires_icloudemail'] = tool.find('Requires.ICloudEmail').text
                vals['requires_icloudphone'] = tool.find('Requires.ICloudPhone').text
                vals['requires_icloududid'] = tool.find('Requires.ICloudUDID').text
                vals['requires_type'] = tool.find('Requires.Type').text
                vals['requires_locks'] = tool.find('Requires.Locks').text
                tool_mobiles = self.get_tool_mobiles(vals['tool_id'])
                mobiles_ids = [int(r.find('ID').text) for r in tool_mobiles.findall('Mobile')]
                vals['product_ids'] = self.env['product.product'].browse(mobiles_ids)
                old_tool = self.env['unlockbase.tool'].search([('tool_id', '=', vals['tool_id'])])
                if len(old_tool) == 1:
                    old_tool.update(vals)
                    _logger.info('Old unlockbase tool updated: %s' % old_tool.name)
                elif len(old_tool) == 0:
                    new_tool = self.env['unlockbase.tool'].create(vals)
                    _logger.info('New unlockbase tool created: %s' % new_tool.name)

    @api.model
    def create_mobiles_tools(self):
        tools = self.env['unlockbase.tool'].browse()
        for tool in tools:
            for mobile_id in tool.product_ids:
                mobile_tools_cat = self.env['product.product'].search([('name', '=', mobile_id.mobile_tech_name)])
                found_tools = self.env['product.product'].search([('unlockbase_tool_id', '=', tool.id), ('categ_id', '=', mobile_tools_cat.id)])
                if len(found_tools) == 0:
                    vals = {'name': tool.name, 'unlockbase_tool_id': tool.id, 'categ_id': mobile_tools_cat.id}
                    new_tool_product = self.env['product.product'].create(vals)
                    _logger.info('New tool product created: %s' % new_tool_product.name)
                elif len(found_tools) == 1:
                    found_tools.update(vals)

    def send_action(self, values):
        values['Key'] = unlockbase_key
        data = urllib.urlencode(values)
        req = urllib2.Request(unlockbase_url, data)
        response = urllib2.urlopen(req)
        the_page = response.read()
        if 'Unauthorized IP address' in the_page:
            _logger.error('Unauthorized IP address ERROR. Please check security configuration in unlockbase.com settings.')
            return False
        res = xml.etree.ElementTree.fromstring(the_page)
        return res

    def get_all_data(self):
        values = {'Action': 'GetMobiles'}
        res = self.send_action(values)
        return res

    def get_tools(self):
        values = {'Action': 'GetTools'}
        res = self.send_action(values)
        return res

    def get_tool_mobiles(self, tool_id):
        values = {'Action': 'GetToolMobiles', 'ID': tool_id}
        res = self.send_action(values)
        return res


class UnlockBaseTool(models.Model):
    _name = 'unlockbase.tool'

    product_ids = fields.One2many('product.product', 'unlockbase_tool_id')
    group_id = fields.Char()
    group_name = fields.Char()
    type = fields.Char()
    tool_id = fields.Char()
    tool_name = fields.Char()
    credits = fields.Float()
    sms = fields.Char()
    message = fields.Char()
    delivery_min = fields.Char()
    delivery_max = fields.Char()
    delivery_unit = fields.Char()
    requires_network = fields.Char()
    requires_mobile = fields.Char()
    requires_provider = fields.Char()
    requires_pin = fields.Char()
    requires_kbh = fields.Char()
    requires_mep = fields.Char()
    requires_prd = fields.Char()
    requires_sn = fields.Char()
    requires_secro = fields.Char()
    requires_reference = fields.Char()
    requires_servicetag = fields.Char()
    requires_icloudemail = fields.Char()
    requires_icloudphone = fields.Char()
    requires_icloududid = fields.Char()
    requires_type = fields.Char()
    requires_lock = fields.Char()


class LoadingThread(threading.Thread):
    def __init__(self, interval, dispatch, threads_bundles_list):
        threading.Thread.__init__(self, name='unlock')
        self.daemon = True

    def run(self):




def make_tech_name(name):
    res = name.strip().lower()
    res = res.replace(' ', '')
    allow = string.letters + string.digits
    re.sub('[^%s]' % allow, '', res)
    return res
