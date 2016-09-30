# -*- coding: utf-8 -*-

from openerp import api, fields, models
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


class ProductCategory(models.Model):
    _inherit = 'product.category'

    brand_id = fields.Char(string='Mobile brand')


class UnlockBase(models.Model):
    _name = 'unlockbase'

    @api.model
    def action_load_from_unlockbase(self):
        _logger.info('Loading of unlockbase.com mobiles database started')
        res = self.check_all()
        if res == 0:
            _logger.error("Please check parser errors")

    @api.model
    def check_all(self):
        res = self.get_all_data()
        mobiles_cat = self.env['product.category'].search([('name', '=', 'Mobiles')], limit=1)
        all_brands = self.env['product.category'].search([('parent_id', '=', mobiles_cat.id)])
        all_brands_names = [r.name for r in all_brands]
        for brand in res.findall('Brand'):
            brand_id = brand.find('ID').text
            brand_name = make_tech_name(brand.find('Name').text)
            old_brand = self.env['product.category'].browse([('name', '=', brand_name)])
            if brand_name not in all_brands_names:
                vals = {'brand_id': brand_id, 'name': brand_name, 'parent_id': mobiles_cat.id}
                # Create brand
                new_cat = self.env['product.category'].create(vals)
                _logger.info('New brand created: %s' % new_cat.name)
            else:
                if not old_brand.brand_id or old_brand.brand_id != brand_id:
                    old_brand.brand_id = brand_id
            for mobile in brand.findall('Mobile'):
                unlock_mobile_id = mobile.find('ID').text
                mobile_name = make_tech_name(mobile.find('Name').text)
                mobile_photo = mobile.find('Photo').text.replace('https', 'http')
                all_brand_mobiles = [r.mobile_tech_name for r in self.env['product.product'].search([('mobile_brand', '=', brand_name)])]
                if mobile_name not in all_brand_mobiles:
                    resp = urllib.urlopen(mobile_photo)
                    photo = None
                    if resp.code == 200:
                        photo = base64.b64encode(resp.read())
                    vals = {'unlock_mobile_id': unlock_mobile_id,
                            'name': mobile_name,
                            'image': photo,
                            'categ_id': brand_id,
                            'sale_ok': False}
                    # Create mobile
                    new_mobile = self.env['product.product'].create(vals)
                    _logger.info('New mobile created: %s %s' % (brand_name, new_mobile.name))
                    # Create category for unlock tools for this phone
                    vals = {'brand_id': brand_id, 'name': mobile_name, 'parent_id': old_brand.id}
                    unlock_cat = self.env['product.category'].create(vals)
                    _logger.info('New unlock_cat created: %s' % unlock_cat.name)
                    # TODO Create unlock tools for this phone
                    # vals = {'brand_id': brand_id, 'name': mobile_name, 'parent_id': old_brand.id}
                    # new_cat = self.env['product.category'].create(vals)
                    # _logger.info('New brand created: %s' % new_cat.name)
                else:
                    old_mobile = self.env['product.product'].browse([('mobile_tech_name', '=', mobile_name)])
                    if not old_mobile.unlock_mobile_id or old_mobile.unlock_mobile_id != unlock_mobile_id:
                        old_mobile.unlock_mobile_id = unlock_mobile_id

    def send_action(self, values):
        values['Key'] = unlockbase_key
        data = urllib.urlencode(values)
        req = urllib2.Request(unlockbase_url, data)
        response = urllib2.urlopen(req)
        the_page = response.read()
        res = xml.etree.ElementTree.fromstring(the_page)
        return res

    def get_all_data(self):
        values = {'Action': 'GetMobiles'}
        res = self.send_action(values)
        return res


def make_tech_name(name):
    res = name.strip().lower()
    res = res.replace(' ', '')
    allow = string.letters + string.digits
    re.sub('[^%s]' % allow, '', res)
    return res
