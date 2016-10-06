# -*- coding: utf-8 -*-

from openerp import api, fields, models
import openerp
import logging
import urllib
import urllib2
import xml.etree.ElementTree
import re
import string


_logger = logging.getLogger("# " + __name__)
_logger.setLevel(logging.DEBUG)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    unlock_mobile_id = fields.Char(string='unlock_mobile_id')
    unlockbase_tool_ids = fields.Many2many('unlockbase.tool', 'unlock_tool_product_rel', 'product_id', 'unlockbase_tool_id')
    unlock_service = fields.Boolean(default=False, help='if this product unlock service or not')


class ProductCategory(models.Model):
    _inherit = 'product.category'

    brand_id = fields.Char(string='Mobile brand')


class UnlockBase(models.Model):
    _name = 'unlockbase'

    unlock_tool_dict = {'tool_id': 'ID',
                'tool_name': 'Name',
                'credits': 'Credits',
                'type': 'Type',
                'sms': 'SMS',
                'message': 'Message',
                'delivery_min': 'Delivery.Min',
                'delivery_max': 'Delivery.Max',
                'delivery_unit': 'Delivery.Unit',
                'requires_network': 'Requires.Network',
                'requires_mobile': 'Requires.Mobile',
                'requires_provider': 'Requires.Provider',
                'requires_pin': 'Requires.PIN',
                'requires_kbh': 'Requires.KBH',
                'requires_mep': 'Requires.MEP',
                'requires_prd': 'Requires.PRD',
                'requires_sn': 'Requires.SN',
                'requires_secro': 'Requires.SecRO',
                'requires_reference': 'Requires.Reference',
                'requires_servicetag': 'Requires.ServiceTag',
                'requires_icloudemail': 'Requires.ICloudEmail',
                'requires_icloudphone': 'Requires.ICloudPhone',
                'requires_icloududid': 'Requires.ICloudUDID',
                'requires_type': 'Requires.Type',
                'requires_locks': 'Requires.Locks',
                }

    @api.model
    def action_load_from_unlockbase(self):
        _logger.info('Loading of unlockbase.com mobiles database started')
        all_good = True
        while all_good:
            all_good = self.create_brands_and_mobiles()  # create, brand, mobile and mobile tools category
            all_good = self.create_tools()   # create tools with bound mobiles to it
            all_good = self.create_mobiles_tools()  # for each mobile we create available unlock tools
            _logger.info('Data from unlockbase.com loaded successfully')
            return
        _logger.info('Errors occurred while unlockbase.com data loading')

    @api.model
    def create_brands_and_mobiles(self):
        res = self.get_all_data()
        if res is False:
            return False
        mobiles_cat = self.env['product.category'].search([('name', '=', 'Mobiles')], limit=1)
        all_brands = self.env['product.category'].search([('parent_id', '=', mobiles_cat.id)])
        all_brands_names = [r.name for r in all_brands]
        for brand in res.findall('Brand'):
            brand_id = brand.find('ID').text
            brand_name_orig = brand.find('Name').text
            brand_name = make_tech_name(brand.find('Name').text)
            all_brand_mobiles = [r.mobile_tech_name for r in self.env['product.product'].search([('mobile_brand', '=', brand_name)])]
            old_brand = self.env['product.category'].search([('name', '=', brand_name)])
            if brand_name not in all_brands_names:
                # TODO TEMP
                continue
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
                    # TODO TEMP
                    continue
                    resp = urllib.urlopen(mobile_photo)
                    photo = None
                    if resp.code == 200:
                        photo = base64.b64encode(resp.read())
                    vals = {'unlock_mobile_id': unlock_mobile_id,
                            'name': brand_name_orig + ' ' + mobile.find('Name').text,
                            'image': photo,
                            'categ_id': categ_to_bind,
                            }
                    # Create mobile
                    new_mobile = self.env['product.product'].create(vals)
                    _logger.info('New mobile created: %s %s' % (brand_name, new_mobile.name))
                else:
                    old_mobile = self.env['product.product'].search([('mobile_tech_name', '=', mobile_name)])
                    if not old_mobile.unlock_mobile_id or old_mobile.unlock_mobile_id != unlock_mobile_id:
                        old_mobile.unlock_mobile_id = unlock_mobile_id
                        _logger.info('Old mobile updated: %s' % old_mobile.name)
                # Create category for unlock tools for this phone
                old_mobile_cat = self.env['product.category'].search([('name', '=', brand_name_orig + ' ' + mobile.find('Name').text)])
                vals = {'brand_id': brand_id,
                        'name': brand_name_orig + ' ' + mobile.find('Name').text,
                        'parent_id': old_brand.id}
                if len(old_mobile_cat) == 1:
                    old_mobile_cat.update(vals)
                    _logger.info('Old unlock mobile tools category updated: %s' % old_mobile_cat.name)
                elif len(old_mobile_cat) == 0:
                    unlock_cat = self.env['product.category'].create(vals)
                    _logger.info('New unlock mobile tools category created: %s' % unlock_cat.name)
                self.env.cr.commit()
        return True

    @api.model
    def create_tools(self):
        tools_list = self.get_tools()
        for group in tools_list.findall('Group'):
            for tool in group.findall('Tool'):
                tool_mobiles = self.get_tool_mobiles(tool.find('ID').text)
                mobiles_ids = [int(r.find('ID').text) for r in tool_mobiles.findall('Mobile')]
                found_mobiles = self.env['product.product'].search([('unlock_mobile_id', 'in', mobiles_ids)])
                if len(found_mobiles) < 1:
                    continue
                vals = {'group_id': group.find('ID').text,  # must have
                        'group_name': group.find('Name').text,  # must have
                        'product_ids': [(6, 0, found_mobiles.ids or [])]}
                for key, val in self.unlock_tool_dict.iteritems():
                    try:
                        vals[key] = tool.find(val).text  # some might absent
                    except:
                        pass
                vals['name'] = tool.find('Name').text
                old_tool = self.env['unlockbase.tool'].search([('name', '=', vals['name'])])
                if len(old_tool) == 1:
                    old_tool.update(vals)
                    _logger.info('Old unlockbase tool updated: %s' % old_tool.name)
                elif len(old_tool) == 0:
                    new_tool = self.env['unlockbase.tool'].create(vals)
                    _logger.info('New unlockbase tool created: %s' % new_tool.name)
                self.env.cr.commit()

    @api.model
    def create_mobiles_tools(self):
        markup = self.env['ir.config_parameter'].sudo().get_param('unlockbase.markup')
        image_path = openerp.modules.get_module_resource('unlockbase', 'static/src/img', 'lock.png')
        mobiles = self.env['product.product'].search([('unlock_mobile_id', '!=', '')])
        for mobile in mobiles:
            mobile_tools_cat = self.env['product.category'].search([('name', '=', mobile.name)])
            for tool in mobile.unlockbase_tool_ids:
                mt_name = mobile.name + '\nTool: \n' + tool.name
                found_tools = self.env['product.product'].search([('name', '=', mt_name), ('categ_id', '=', mobile_tools_cat.id)])
                vals = {'name': mt_name,
                        'unlockbase_tool_ids': [(4, tool.id,)],
                        'type': 'service',
                        'unlock_service': True,
                        'standard_price': tool.credits,
                        'list_price': tool.credits * (1+(markup/100)),
                        'image': open(image_path, 'rb').read().encode('base64'),
                        'categ_id': mobile_tools_cat.id}
                if len(found_tools) == 0:
                    new_tool_product = self.env['product.product'].create(vals)
                    _logger.info('New unlockbase tool product created: %s' % new_tool_product.name)
                elif len(found_tools) == 1:
                    found_tools.update(vals)
                    _logger.info('Old unlockbase tool product updated: %s' % found_tools.name)
                self.env.cr.commit()

    """ unlockbase.com API v3 representation """

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

    def send_action(self, values):
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


class UnlockBaseTool(models.Model):
    _name = 'unlockbase.tool'

    product_ids = fields.Many2many('product.product', 'unlock_tool_product_rel', 'unlockbase_tool_id', 'product_id')
    name = fields.Char()
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
    IMEI = fields.Char()
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
    requires_locks = fields.Char()


def make_tech_name(name):
    res = name.strip().lower()
    res = res.replace(' ', '')
    allow = string.letters + string.digits
    re.sub('[^%s]' % allow, '', res)
    return res


def dump(obj):
  for attr in dir(obj):
    print "obj.%s = %s" % (attr, getattr(obj, attr))


def dumpclean(obj):
    if type(obj) == dict:
        for k, v in obj.items():
            if hasattr(v, '__iter__'):
                print k
                dumpclean(v)
            else:
                print '%s : %s' % (k, v)
    elif type(obj) == list:
        for v in obj:
            if hasattr(v, '__iter__'):
                dumpclean(v)
            else:
                print v
    else:
        print obj
