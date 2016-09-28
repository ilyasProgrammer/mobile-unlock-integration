# -*- coding: utf-8 -*-

from openerp import api, fields, models
import logging
import urllib
import urllib2
import xml.etree.ElementTree
import base64

_logger = logging.getLogger("# " + __name__)
_logger.setLevel(logging.DEBUG)

url = 'http://www.unlockbase.com/xml/api/v3'
Key = '(C8C7-4533-06AE-3151)'


class ProductProduct(models.Model):
    _inherit = 'product.product'

    mobile_id = fields.Char(string='Mobile id to unlock')


class ProductCategory(models.Model):
    _inherit = 'product.category'

    brand_id = fields.Char(string='Mobile brand id to unlock')


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def create_from_ui(self, cr, uid, context):
        res = super(PosOrder, self).create_from_ui(cr, uid, context)
        unlock_product = self.pool['product.product'].search(cr, uid, [('name', '=', 'unlock')])
        for order in context:
            for line in order['data']['lines']:
                if 1:
                    self.check_db(cr, uid, context)
        return res

    def check_db(self, cr, uid, context):
        res = self.GetMobiles(cr, uid, context)
        mobiles_cat = self.pool['product.category'].search(cr, uid, [('name', '=', 'Mobiles')], limit=1)
        if len(mobiles_cat) < 1:
            return
        mobiles_cat_id = mobiles_cat[0]
        all_brands_ids = self.pool['product.category'].search(cr, uid, [('parent_id', '=', mobiles_cat_id)])
        all_brands = [r.brand_id for r in self.pool['product.category'].browse(cr, uid, all_brands_ids)]
        all_mobiles_ids = self.pool['product.product'].search(cr, uid, [('mobile_id', '!=', '')])
        all_mobiles = [r.mobile_id for r in self.pool['product.product'].browse(cr, uid, all_mobiles_ids)]
        for brand in res.findall('Brand'):
            brand_id = brand.find('ID').text
            brand_name = brand.find('Name').text
            if brand_id not in all_brands:
                vals = {'brand_id': brand_id, 'name': brand_name, 'parent_id': mobiles_cat_id}
                new_cat = self.pool['product.category'].create(cr, uid, vals)
                _logger.info('New brand created: %s' % brand_name)
            for mobile in brand.findall('Mobile'):
                mobile_id = mobile.find('ID').text
                mobile_name = mobile.find('Name').text
                mobile_photo = mobile.find('Photo').text.replace('https', 'http')
                if mobile_id not in all_mobiles:
                    resp = urllib.urlopen(mobile_photo)
                    img = None
                    if resp.code == 200:
                        img = base64.b64encode(resp.read())
                    vals = {'mobile_id': mobile_id, 'name': mobile_name, 'image': img, 'categ_id': brand_id, 'sale_ok': False}
                    new_mobile = self.pool['product.product'].create(cr, uid, vals)
                    _logger.info('New mobile created: %s %s' % (brand_name, mobile_name))
                    return

    def send_action(self, values, cr, uid, context):
        values['Key'] = Key
        data = urllib.urlencode(values)
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        the_page = response.read()
        res = xml.etree.ElementTree.fromstring(the_page)
        return res

    def place_order(self):
        values = {'Key': Key,
                  'Action': 'PlaceOrder'}

        data = urllib.urlencode(values)
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        the_page = response.read()
        print the_page

    def account_info(self):
        values = {'Key': Key,
                  'Action': 'AccountInfo'}

        data = urllib.urlencode(values)
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        the_page = response.read()
        print the_page

        values = {'Key': Key,
                  'Action': 'GetMobiles '}

    def get_mobiles (self, cr, uid, context):
        values = {'Action': 'GetMobiles'}
        res = self.send_action(values, cr, uid, context)
        return res