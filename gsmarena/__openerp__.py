# -*- coding: utf-8 -*-
{
    "name": """gsmarena data load""",
    "summary": """Load mobiles data form gsmarena.com""",
    "description": """Load mobiles data form gsmarena.com""",
    "category": "Web",
    "images": [],
    "version": "1.0.0",

    "author": "Ilyas",
    "website": "",
    "license": "GPL-3",
    #"price": 9.00,
    #"currency": "EUR",

    "depends": [
        "base",
        "product",
    ],
    "external_dependencies": {'python': ['bs4']},
    "data": [
        "data/ir_action_server.xml",
        "data/product_category.xml",
        "data/cron.xml",
    ],
    "qweb": [
    ],
    "demo": [
    ],

    'post_load' : '',
    "pre_init_hook": None,
    "post_init_hook": None,
    "installable": True,
    "auto_install": False,

}
