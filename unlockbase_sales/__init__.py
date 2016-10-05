# -*- encoding: utf-8 -*-

import logging
import unlockbase_sales
from openerp import SUPERUSER_ID

_logger = logging.getLogger("# " + __name__)
_logger.setLevel(logging.DEBUG)


def _set_pos_category(cr, registry):
    root = registry['pos.category'].search(cr, SUPERUSER_ID, [('name', '=', 'Mobile unlock')])
    mobiles_tools_ids = registry['product.product'].search(cr, SUPERUSER_ID, [('unlock_service', '=', True)])
    mobiles_tools = registry['product.product'].browse(cr, SUPERUSER_ID, mobiles_tools_ids)
    for mobile_tool in mobiles_tools:
        if len(mobile_tool.pos_categ_id) == 0:
            old_pos_cat = registry['pos.category'].search(cr, SUPERUSER_ID, [('name', '=', mobile_tool.categ_id.name)])
            if len(old_pos_cat) == 0:
                vals = {'name': mobile_tool.categ_id.name, 'parent_id': root[0]}
                new_pos_cat = registry['pos.category'].create(cr, SUPERUSER_ID, vals)
                _logger.info('New pos category created %s' % mobile_tool.categ_id.name)
                mobile_tool.pos_categ_id = new_pos_cat
            elif len(old_pos_cat) == 1:
                mobile_tool.pos_categ_id = old_pos_cat
                _logger.info('Mobile tool updated %s' % mobile_tool.name)
            cr.commit()
