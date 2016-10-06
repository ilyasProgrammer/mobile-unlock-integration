# -*- coding: utf-8 -*-

from openerp import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class ProductPrice(models.TransientModel):
    _name = 'product.prices'

    markup = fields.Float(string='Mark-up', default=10)

    @api.multi
    def set_prices(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        active_model = context.get('active_model', None)
        for rec in self.env[active_model].browse(active_ids):
            if rec.standard_price != 0:
                rec.list_price = rec.standard_price * (1+(self.markup/100))
                _logger.info('%s new price = %s' % (rec.name, rec.list_price))
        return
