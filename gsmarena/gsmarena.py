# -*- coding: utf-8 -*-

from openerp import api, fields, models
import logging
import urllib
import urllib2
import xml.etree.ElementTree
import base64
import re
from bs4 import BeautifulSoup as bs
import string

_logger = logging.getLogger("# " + __name__)
_logger.setLevel(logging.DEBUG)

brands = ['Nokia']  # TODO load brands from somewhere
# brands = ['Nokia', 'Apple', 'Acer', 'Huawei']


class ProductProduct(models.Model):
    _inherit = 'product.product'

    mobile_id = fields.Char(string='Mobile id')  # gsmarena mobile id
    mobile_brand = fields.Char(string='Mobile brand')
    mobile_title = fields.Char(string='Mobile title')
    mobile_slug = fields.Char(string='Mobile slug')
    mobile_tech_name = fields.Char(string='Mobile name for binding')


class GsmArena(models.Model):
    _name = 'gsmarena'

    @api.model
    def action_load_from_gsmarena(self):
        _logger.info('Loading of gsmarena.com mobiles database started')
        all_good = True
        while all_good:
            all_good = self.check_brands()
            all_good = self.check_mobiles()
            return
        _logger.error("Please check gsmarena mobiles parser errors")

    @api.model
    def check_mobiles(self):
        mobiles_dict = self.get_gsmarena_mobiles()
        if mobiles_dict is False:
            return False
        for key, value in mobiles_dict.iteritems():
            found_mobiles = self.env['product.product'].search([('mobile_id', '=', key)])
            if len(found_mobiles) == 0:
                # create new
                categ = self.env['product.category'].search([('name', '=', value['brand'])])
                if len(categ) != 1:
                    # error TODO
                    return
                vals = {'mobile_id': value['id'],
                        'name': value['name'],
                        'mobile_tech_name': value['mobile_tech_name'],
                        'mobile_brand': value['brand'],
                        'mobile_slug': value['slug'],
                        'mobile_title': value['title'],
                        'image': value['photo'],
                        'categ_id': categ.id}
                new_mobile = self.env['product.product'].create(vals)
                _logger.info('New mobile added: %s' % new_mobile.name)
            elif len(found_mobiles) == 1:
                found_mobiles.update(vals)
                _logger.info('Old mobile updated: %s' % found_mobiles.name)
        return True

    @api.model
    def check_brands(self):
        mobiles_cat = self.env['product.category'].search([('name', '=', 'Mobiles')], limit=1)
        all_brands = self.env['product.category'].search([('parent_id', '=', mobiles_cat.id)])
        all_brands_names = [r.name for r in all_brands]
        for brand in brands:
            if brand not in all_brands_names:
                vals = {'brand_id': '', 'name': make_tech_name(brand), 'parent_id': mobiles_cat.id}
                new_cat = self.env['product.category'].create(vals)
                _logger.info('New mobile brand added: %s' % new_cat.name)
            else:
                # TODO check accordance
                pass
        return True

    @api.model
    def get_gsmarena_mobiles(self):
        # returns  dict of dict {mobile_id:{'name':'', 'photo': '', ... }}
        gsmarena_url = self.env['ir.config_parameter'].sudo().get_param('gsmarena.url')
        ret = dict()
        simbol = ["&", "+"]
        kata = ["_and_", "_plus_"]
        values = {'sQuickSearch': 'yes'}
        for brand in brands:
            values['sName'] = brand
            page = get_http_page(gsmarena_url, values)
            soup = bs(page, 'html.parser')
            makers = soup.find_all('div', 'makers')
            if len(makers) != 1:
                print 'Error get_gsmarena_mobiles'  # TODO
                return False
            mobiles = makers[0].find_all('li')
            for r in mobiles:
                mobile = dict()
                mobile['name'] = brand + ' ' + r.find('br').text
                mobile['mobile_tech_name'] = make_tech_name(r.find('br').text)
                mobile['brand'] = make_tech_name(brand)
                mobile['title'] = r.find('img').attrs['title']
                mobile['slug'] = r.find('a').attrs['href'].replace('.php', '')
                resp = urllib.urlopen(r.find('img').attrs['src'])
                photo = None
                if resp.code == 200:
                    photo = base64.b64encode(resp.read())
                mobile['photo'] = photo
                mob_id = self.get_mobile_id('http://www.gsmarena.com/' + r.find('a').attrs['href'])
                if mob_id is False:
                    print 'Cant parse mobile id in get_gsmarena_mobiles'  # TODO
                    return False
                mobile['id'] = mob_id
                ret[mobile['id']] = mobile
        return ret

    @api.model
    def get_mobile_id(self, url):
        # get gsmarena mobile ID that placed in script field
        page = get_http_page(url)
        soup = bs(page, 'html.parser')
        scripts = soup.find_all('script', attrs={"type": "text/javascript", "language": "javascript"})
        try:
            for script in scripts:
                res = script.text.find('HISTORY_ITEM_ID')
                if res > 0:
                    for spl in re.split(';', script.text):
                        if spl.find('HISTORY_ITEM_ID') > 0:
                            mobile_id = re.findall('\d+', spl)[0]
                            break
        except:
            _logger.error("Mobile ID parsing error !")
            return False
        return int(mobile_id)


def get_http_page(url, params=None):
    # url - to load page from
    # params - dict
    if params:
        params = urllib.urlencode(params)
    req = urllib2.Request(url, params)
    response = urllib2.urlopen(req)
    page = response.read()
    return page


def make_tech_name(name):
    res = name.strip().lower()
    res = res.replace(' ', '')
    allow = string.letters + string.digits
    re.sub('[^%s]' % allow, '', res)
    return res
